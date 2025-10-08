from .models import Video
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class VideoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_video(self, user_id, title, description, file_url):
        video = Video(
            user_id=user_id, title=title, description=description, file_url=file_url
        )

        self.db.add(video)
        await self.db.commit()
        await self.db.refresh(video)
        return video

    async def get_user_videos(self, user_id):
        result = await self.db.execute(select(Video).where(Video.user_id == user_id))

        return result.scalars().all()
