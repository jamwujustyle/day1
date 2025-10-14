from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from .models import MagicLink
from app.users.models import User


class MagicAuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_magic_link(
        self, email: str, otp: str, token: str, expires_at: datetime
    ) -> MagicLink:
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

    async def get_magic_link_by_token(self, token: str) -> MagicLink:
        link = await self.db.execute(select(MagicLink).where(MagicLink.token == token))

        return link.scalar_one_or_none()

    async def get_or_create_user(self, email: str):
        base_username = email.split("@")[0]
        result = await self.db.execute(
            select(User).where((User.email == email) & (User.username == base_username))
        )

        user = result.scalar_one_or_none()

        if not user:
            user = User(email=email, username=base_username)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def get_magic_link_by_email_and_otp(
        self, email: str, otp_code: str
    ) -> MagicLink:
        query = select(MagicLink).where(
            func.lower(MagicLink.email) == email.lower(),
            MagicLink.otp == otp_code,
            MagicLink.used == False,
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()
