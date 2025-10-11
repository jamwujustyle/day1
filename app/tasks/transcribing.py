from celery import shared_task, group
from sqlalchemy import select

from app.videos.models.subtitle import Subtitle
from app.videos.services.subtitle import SubtitleService

from ..configs.database import SyncSessionLocal
from . import OPENAI_KEY, LANGUAGE_MAP

import os
import openai


openai.api_key = OPENAI_KEY


@shared_task
def transcribe_to_language(video_id: str, language: str, lang_code: str):
    db = SyncSessionLocal()

    try:
        from app.videos.models.video import Video

        video = db.execute(select(Video).where(Video.id == video_id)).scalar_one()

        existing = db.execute(
            select(Subtitle).where(
                (Subtitle.video_id == video_id) & (Subtitle.language == language)
            )
        ).scalar_one_or_none()

        if existing:
            print("Subtitle already exists")
            return

        audio_path = f"/tmp/{video_id}_audio_{lang_code}.wav"

        from moviepy import VideoFileClip

        clip = VideoFileClip(video.file_url)
        clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
        clip.close()

        with open(audio_path, "rb") as file:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=file,
                language=lang_code,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )
        subtitle_service = SubtitleService(db)
        subtitle = subtitle_service.create_subtitle_from_transcription(
            transcription_data=transcription, video_id=video_id, language=language
        )

    except Exception as ex:
        db.rollback()
        print(f"Error transcribing {language}: {ex}")
        raise ex
    finally:
        db.close()


@shared_task
def generate_subtitles_for_video(video_id: str):
    transcribe_tasks = group(
        transcribe_to_language.s(video_id, language, lang_code)
        for language, lang_code in LANGUAGE_MAP.items()
    )
    result = transcribe_tasks.apply_sync()

    print(f"started concurrent transcription for video: {video_id}")

    return result.id
