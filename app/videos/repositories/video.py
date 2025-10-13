from ..models.video import Video
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


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
            .options(selectinload(Video.subtitles), selectinload(Video.localizations))
        )

        return result.scalars().all()
