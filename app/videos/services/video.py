import os
import uuid
import shutil
from typing import List
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ...users.models import User
from ..schemas.video import VideoResponse
from ..repositories.video import VideoRepository

from app.celery_app import celery_app


class VideoService:
    def __init__(self, db: AsyncSession):
        self.repo = VideoRepository(db)

    async def upload_video(
        self,
        user: User,
        file: UploadFile,
    ) -> VideoResponse:

        temp_path = f"/tmp/{uuid.uuid4()}.{file.filename.split('.')[-1]}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        video = await self.repo.create_video(user_id=user.id, file_url="pending")
        celery_app.send_task(
            "app.tasks.trimming.trim_silence", args=[temp_path, str(video.id)]
        )

        return VideoResponse.model_validate(video)

    async def get_user_videos(self, user_id) -> List[VideoResponse]:
        videos = await self.repo.get_user_videos(user_id=user_id)

        return [VideoResponse.model_validate(v) for v in videos]
