from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from uuid import UUID
from typing import List, Optional

from ..models import UserBio


class UserBioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_bio(self, user_id: UUID, bio: str) -> UserBio:
        result = await self.db.execute(
            select(UserBio).where(UserBio.user_id == user_id)
        )

        existing = result.scalar_one_or_none()

        if existing:
            existing.bio = bio
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            new_bio = UserBio(user_id=user_id, bio=bio)
            self.db.add(new_bio)
            await self.db.commit()
            await self.db.refresh(new_bio)
            return new_bio

    async def fetch_user_bio(self, user_id: UUID) -> Optional[UserBio]:
        bio = await self.db.execute(
            select(UserBio.bio).where(UserBio.user_id == user_id)
        )

        return bio.scalar_one_or_none()
