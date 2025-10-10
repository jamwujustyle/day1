import os
import time
import uuid
from io import BytesIO
from celery import shared_task
from elevenlabs.client import ElevenLabs
from decouple import config

from ..configs.database import SyncSessionLocal
from ..videos.models.video import LocalizedVideo

MEDIA_ROOT = "media/videos"

# It's better to load keys from environment variables
# Make sure these are set in your .env file or environment
LAB_KEY = config("ELEVENLABS_API_KEY", default="")

lab_client = ElevenLabs(api_key=LAB_KEY)

# Mapping from full language names to two-letter codes used by ElevenLabs
LANGUAGE_MAP = {
    "english": "en",
    "spanish": "es",
    "mandarin": "zh",
    "french": "fr",
    "hindi": "hi",
    "russian": "ru",
}


@shared_task
def dub_audio(audio_path: str, target_lang: str, video_id: str):
    """
    Celery task to dub an audio file to a target language and save it to the database.
    """
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return

    db = SyncSessionLocal()
    try:
        with open(audio_path, "rb") as f:
            file_data = BytesIO(f.read())

        file_name = os.path.basename(audio_path)
        file_data.name = file_name

        print(f"Starting dubbing job for {file_name} to '{target_lang}'...")

        dubbing_job = lab_client.dubbing.create(
            file=file_data,
            target_lang=target_lang,
            disable_voice_cloning=False,
            watermark=False,
            highest_resolution=True,
        )
        dubbing_id = dubbing_job.dubbing_id

        # Poll for status until the dubbing is complete
        while True:
            status = lab_client.dubbing.get(dubbing_id).status
            if status == "dubbed":
                print(f"Dubbing to '{target_lang}' complete. Downloading...")
                dubbed_file = lab_client.dubbing.audio.get(dubbing_id, target_lang)

                # Define output path within the video-specific directory
                video_dir = os.path.join(MEDIA_ROOT, str(video_id))
                os.makedirs(video_dir, exist_ok=True)
                output_filename = f"{target_lang}.wav"
                output_path = os.path.join(video_dir, output_filename)

                with open(output_path, "wb") as out_f:
                    for chunk in dubbed_file:
                        out_f.write(chunk)

                print(f"Dubbed audio saved to {output_path}")

                # Save to database
                new_localized_video = LocalizedVideo(
                    video_id=video_id,
                    language=target_lang,
                    file_url=f"/{output_path}",
                )
                db.add(new_localized_video)
                db.commit()
                print(
                    f"Saved localized video for language '{target_lang}' to database."
                )
                break
            elif status in ["dubbing", "pending"]:
                print(
                    f"Audio is still being dubbed to '{target_lang}'... current status: {status}"
                )
                time.sleep(10)  # Increased sleep time for polling
            else:
                print(f"Dubbing job failed with status: {status}")
                break
    except Exception as e:
        db.rollback()
        print(f"An error occurred during dubbing to '{target_lang}': {e}")
        raise
    finally:
        db.close()
