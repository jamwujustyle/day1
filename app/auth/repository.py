from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from .models import MagicLink


class MagicAuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_magic_link(
        self, email: str, otp: str, token: str, expires_at: datetime
    ):
        link = MagicLink(
            email=email,
            otp=otp,
            token=token,
            expires_at=expires_at,
        )
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)

        return link
