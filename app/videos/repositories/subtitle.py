from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.subtitle import Subtitle
from uuid import UUID


class SubtitleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_subtitle(self, language, text, segments, video_id) -> Subtitle:
        subtitle = Subtitle(
            language=language, text=text, segments=segments, video_id=video_id
        )

        self.db.add(subtitle)
        await self.db.commit()
        await self.db.refresh(subtitle)

        return subtitle

    async def get_subtitle(self, language, video_id) -> Subtitle:
        subtitle = await self.db.execute(
            select(Subtitle).where(
                (Subtitle.video_id == video_id) & (Subtitle.language == language)
            )
        )

        return subtitle.scalar_one_or_none()

    async def get_subtitle_by_id(self, subtitle_id: UUID) -> Subtitle:
        result = await self.db.execute(
            select(Subtitle).where(Subtitle.id == subtitle_id)
        )
        return result.scalar_one_or_none()
