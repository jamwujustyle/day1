import asyncio
import openai
from celery import shared_task
from app.configs.database import AsyncSessionLocal
from app.videos.services import SubtitleService, VideoService
from app.videos.schemas.ai import AITranslation, AISegment
from .transcribing import generate_subtitles_for_video


@shared_task
def transcribe_source_audio(video_id: str, audio_path: str):
    """
    Transcribes the audio, creates the source subtitle, and triggers the translation tasks.
    """
    with open(audio_path, "rb") as audio_file:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
        source_lang = transcription.language
        print(f"Detected language: {source_lang}")

        # Save the source subtitle
        async def process_subtitle():
            async with AsyncSessionLocal() as async_db:
                subtitle_service = SubtitleService(async_db)
                video_service = VideoService(async_db)

                # Adapt the Whisper response to the AITranslation schema
                ai_translation = AITranslation(
                    title="",  # No title from Whisper
                    summary="",  # No summary from Whisper
                    text=transcription.text,
                    segments=[
                        AISegment(word=w.word, start=w.start, end=w.end)
                        for w in transcription.words
                    ],
                )

                await subtitle_service.create_subtitle_from_transcription(
                    transcription_data=ai_translation,
                    video_id=video_id,
                    language=source_lang,
                )

                video = await video_service.get_video_by_id(video_id=video_id)
                video.source_language = source_lang
                await async_db.commit()

        asyncio.run(process_subtitle())

    # Trigger the next step in the pipeline
    generate_subtitles_for_video.delay(video_id=video_id, source_language=source_lang)
