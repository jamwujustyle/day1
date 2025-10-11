from celery import shared_task
from decouple import config

from app.videos.models.subtitle import Subtitle
from ..configs.database import SyncSessionLocal

import os
import openai


MEDIA_ROOT = "media/videos"
LAB_KEY = config("ELEVENLABS_API_KEY", default="")
OPENAI_KEY = config("OPENAI_API_KEY", default="")

openai.api_key = OPENAI_KEY


@shared_task
def transcribe_dubbed_audio(audio_path: str, language: str, video_id: str):
    """Transcribe dubbed audio and save as subtitle"""
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return

    db = SyncSessionLocal()
    try:
        with open(audio_path, "rb") as f:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
            )

        # Save subtitle to media/subtitles
        subtitle_dir = os.path.join("media/subtitles", str(video_id))
        os.makedirs(subtitle_dir, exist_ok=True)
        subtitle_filename = f"{language}.txt"
        subtitle_path = os.path.join(subtitle_dir, subtitle_filename)

        with open(subtitle_path, "w") as f:
            f.write(transcription)

        # Save to database
        subtitle = Subtitle(
            video_id=video_id,
            language=language,
            file_url=f"/{subtitle_path}",
        )
        db.add(subtitle)
        db.commit()
        print(f"Subtitle for '{language}' saved to {subtitle_path}")

    except Exception as e:
        db.rollback()
        print(f"Error transcribing '{language}': {e}")
        raise
    finally:
        db.close()
