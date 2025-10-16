from moviepy import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment, silence
from celery import shared_task

import os
import uuid
import openai
import json
from decouple import config

import asyncio
from ..configs.database import AsyncSessionLocal
from ..videos.services import VideoService


MEDIA_ROOT = "media/videos"
OPENAI_KEY = config(
    "OPENAI_API_KEY",
    default="",
)
openai.api_key = OPENAI_KEY


@shared_task
def trim_silence(temp_path: str, video_id: str):
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

        async def update_video_url():
            async with AsyncSessionLocal() as async_db:
                video_service = VideoService(async_db)
                await video_service.update_video_url(
                    video_id=video_id, file_url=final_path
                )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(update_video_url())

        # Language detection and dubbing
        trimmed_audio_path = f"/tmp/trimmed_audio_for_dubbing_{unique_id}.wav"
        trimmed_video_for_audio = VideoFileClip(final_path)
        trimmed_video_for_audio.audio.write_audiofile(trimmed_audio_path)
        trimmed_video_for_audio.close()

        from .speech_to_text import transcribe_source_audio

        transcribe_source_audio.delay(video_id=video_id, audio_path=trimmed_audio_path)

        # Clean up temporary audio files
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

    except Exception as ex:
        raise ex
