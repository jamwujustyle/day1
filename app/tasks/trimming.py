from moviepy import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment, silence
from celery import shared_task
from sqlalchemy import select
import os
import uuid


from ..videos.services.video import VideoService
from ..videos.models.video import Video
from ..configs.database import SyncSessionLocal

MEDIA_ROOT = "media/videos"


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

        os.makedirs(MEDIA_ROOT, exist_ok=True)
        final_filename = f"{uuid.uuid4()}.mp4"
        final_path = os.path.join(MEDIA_ROOT, final_filename)

        trimmed_video.write_videofile(final_path, codec="libx264", audio_codec="aac")

        clip.close()
        trimmed_video.close()
        os.remove(temp_path)

        video = db.execute(select(Video).where(Video.id == video_id)).scalar_one()
        video.file_url = f"/{final_path}"
        db.commit()

    except Exception as ex:
        db.rollback()
        raise ex
    finally:
        db.close()
