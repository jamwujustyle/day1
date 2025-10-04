from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Optional
import uuid

from .models import SocialAccount


class SocialAccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[SocialAccount]:
        result = await self.db.execute(
            select(SocialAccount).where(SocialAccount.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[SocialAccount]:
        result = await self.db.execute(
            select(SocialAccount).where(SocialAccount.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_provider_data(
        self, social_account_id: uuid.UUID, provider_data: dict
    ) -> Optional[SocialAccount]:
        result = await self.db.execute(
            select(SocialAccount).where(SocialAccount.id == social_account_id)
        )
        social_account = result.scalar_one_or_none()

        if social_account:
            social_account.provider_data = provider_data
            await self.db.commit()
            await self.db.refresh(social_account)

        return social_account

    async def create(
        self, user_id: uuid.UUID, email: str, provider_data: dict
    ) -> SocialAccount:
        social_account = SocialAccount(
            user_id=user_id, email=email, provider_data=provider_data
        )
        await self.db.add(social_account)
        await self.db.refresh(social_account)
        return social_account
