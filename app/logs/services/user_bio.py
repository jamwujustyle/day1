from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import UserBioRepository
from ..models import UserBio


from typing import List
from uuid import UUID


class UserBioService:
    def __init__(self, db: AsyncSession):
        self.repo = UserBioRepository(db)

    async def get_or_create_bio(self, user_id: UUID, bio: str) -> UserBio:
        await self.repo.get_or_create_bio(user_id=user_id, bio=bio)

    async def fetch_user_bio(self, user_id: UserBio):
        return await self.repo.fetch_user_bio(user_id)
