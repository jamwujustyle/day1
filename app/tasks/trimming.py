from moviepy import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment, silence
from celery import shared_task
from sqlalchemy import select

import os
import uuid
import openai
import json
from decouple import config

from ..configs.database import SyncSessionLocal
from ..videos.models.video import Video

from app.videos.services.subtitle import SubtitleService

MEDIA_ROOT = "media/videos"
OPENAI_KEY = config(
    "OPENAI_API_KEY",
    default="",
)
openai.api_key = OPENAI_KEY


@shared_task
def trim_silence(temp_path: str, video_id: str):
    db = SyncSessionLocal()

    # Add unique identifier to prevent file conflicts
    unique_id = str(uuid.uuid4())
    temp_audio_path = f"/tmp/temp_audio_{unique_id}.wav"

    try:
        clip = VideoFileClip(temp_path)
        clip.audio.write_audiofile(temp_audio_path)

        audio = AudioSegment.from_wav(temp_audio_path)
        chunks = silence.detect_nonsilent(
            audio,
            min_silence_len=1000,
            silence_thresh=audio.dBFS - 14,
        )

        timestamps = [(start / 1000, end / 1000) for start, end in chunks]
        subclips = [clip.subclipped(start, end) for start, end in timestamps]

        trimmed_video = concatenate_videoclips(subclips)

        # Create a dedicated directory for the video using its ID
        video_dir = os.path.join(MEDIA_ROOT, str(video_id))
        os.makedirs(video_dir, exist_ok=True)

        final_filename = "original.mp4"
        final_path = os.path.join(video_dir, final_filename)

        trimmed_video.write_videofile(final_path, codec="libx264", audio_codec="aac")

        clip.close()
        trimmed_video.close()
        os.remove(temp_path)

        video = db.execute(select(Video).where(Video.id == video_id)).scalar_one()
        video.file_url = final_path
        db.commit()

        # Language detection and dubbing
        trimmed_audio_path = f"/tmp/trimmed_audio_for_dubbing_{unique_id}.wav"
        trimmed_video_for_audio = VideoFileClip(final_path)
        trimmed_video_for_audio.audio.write_audiofile(trimmed_audio_path)
        trimmed_video_for_audio.close()

        with open(trimmed_audio_path, "rb") as audio_file:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )
            source_lang = transcription.language
            print(f"Detected language: {source_lang}")

            # Use async session for SubtitleService
            from app.configs.database import AsyncSessionLocal
            import asyncio

            # Properly await the async method
            async def process_subtitle():
                async with AsyncSessionLocal() as async_db:
                    subtitle_service = SubtitleService(async_db)
                    await subtitle_service.create_subtitle_from_transcription(
                        transcription_data=transcription,
                        video_id=video_id,
                        language=source_lang,
                    )

            asyncio.get_event_loop().run_until_complete(process_subtitle())

            video.source_language = source_lang
            db.commit()

            # Generate title and summary for the source language
            prompt = f"""
            Based on the following text, please generate a suitable title (maximum 70 characters) and a concise summary in {source_lang}.
            The title and summary should be written in the first person, as if the speaker in the video is writing them.

            Text:
            {transcription.text}

            Please provide the output in a single JSON object with the following keys:
            - "title": "Generated title in {source_lang} (maximum 70 characters)"
            - "summary": "Generated summary in {source_lang}"
            """

            response = openai.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates titles and summaries in JSON format.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            # Create a VideoLocalization for the source language
            from app.videos.models import VideoLocalization

            source_localization = VideoLocalization(
                video_id=video_id,
                language=source_lang,
                title=result["title"],
                summary=result["summary"],
            )
            db.add(source_localization)
            db.commit()

        # Clean up temporary audio files
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if os.path.exists(trimmed_audio_path):
            os.remove(trimmed_audio_path)

        from app.tasks.transcribing import generate_subtitles_for_video

        generate_subtitles_for_video.delay(
            video_id=video_id, source_language=source_lang
        )

    except Exception as ex:
        db.rollback()
        raise ex
    finally:
        db.close()
