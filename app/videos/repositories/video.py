from ..models import Video, VideoLocalization
from app.logs.models import Thread, Log
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from uuid import UUID


class VideoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_video(self, user_id, file_url):
        video = Video(user_id=user_id, file_url=file_url)

        self.db.add(video)
        await self.db.commit()
        await self.db.refresh(video)

        return video

    async def get_user_videos(self, user_id):
        result = await self.db.execute(
            select(Video)
            .where(Video.user_id == user_id)
            .options(
                selectinload(Video.subtitles),
                selectinload(Video.localizations),
                selectinload(Video.log).selectinload(Log.thread),
            )
        )

        return result.scalars().all()

    async def get_video_by_id(self, video_id: UUID):

        video = await self.db.execute(select(Video).where(Video.id == video_id))

        return video.scalar_one_or_none()

    async def create_localization(
        self, video_id: UUID, language: str, title: str, summary: str
    ) -> VideoLocalization:
        video_localization = VideoLocalization(
            video_id=video_id, language=language, title=title, summary=summary
        )

        self.db.add(video_localization)
        await self.db.commit()
        await self.db.refresh(video_localization)

        return video_localization

    async def update_video_url(self, video_id: UUID, file_url: str) -> Video:
        video = await self.get_video_by_id(video_id)
        if video:
            video.file_url = file_url
            await self.db.commit()
            await self.db.refresh(video)
        return video
