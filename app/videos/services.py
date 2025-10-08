import os
import shutil
import uuid
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..users.models import User

from .schemas import VideoResponse
from .repository import VideoRepository

MEDIA_ROOT = "media/videos"


class VideoService:
    def __init__(self, db: AsyncSession):
        self.repo = VideoRepository(db)

    async def upload_video(
        self, user: User, file: UploadFile, title: str, description: str
    ) -> VideoResponse:
        os.makedirs(MEDIA_ROOT, exist_ok=True)

        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(MEDIA_ROOT, unique_filename)
        file_url = f"/{file_path}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        video = await self.repo.create_video(
            user_id=user.id,
            title=title,
            description=description,
            file_url=file_url,
        )

        return VideoResponse.model_validate(video)

    async def get_user_videos(self, user_id) -> List[VideoResponse]:
        videos = await self.repo.get_user_videos(user_id=user_id)

        return [VideoResponse.model_validate(v) for v in videos]
