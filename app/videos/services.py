from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..users.models import User

from .schemas import VideoCreate, VideoResponse
from .repository import VideoRepository


class VideoService:
    def __init__(self, db: AsyncSession):
        self.repo = VideoRepository(db)

    async def upload_video(self, user: User, payload: VideoCreate) -> VideoResponse:
        video = await self.repo.create_video(
            user_id=user.id,
            title=payload.title,
            description=payload.description,
            file_url=payload.file_url,
        )

        return VideoResponse.model_validate(video)

    async def get_user_videos(self, user_id) -> List[VideoResponse]:
        videos = await self.repo.get_user_videos(user_id=user_id)

        return [VideoResponse.model_validate(v) for v in videos]
