from moviepy import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment, silence
from celery import shared_task
from sqlalchemy import select

import os
import openai
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

    try:
        clip = VideoFileClip(temp_path)
        clip.audio.write_audiofile("/tmp/temp_audio.wav")

        audio = AudioSegment.from_wav("/tmp/temp_audio.wav")
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
        trimmed_audio_path = "/tmp/trimmed_audio_for_dubbing.wav"
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

            subtitle_service = SubtitleService(db)
            subtitle = subtitle_service.create_subtitle_from_transcription(
                transcription_data=transcription,
                video_id=video_id,
                language=source_lang,
            )
            print(f"Detected language: {source_lang}")

            video.language = source_lang

            db.commit()
        from app.tasks.transcribing import generate_subtitles_for_video

        generate_subtitles_for_video.delay(video_id)

    except Exception as ex:
        db.rollback()
        raise ex
    finally:
        db.close()
