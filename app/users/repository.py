from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import User

from typing import Optional
import uuid

from datetime import datetime, timezone


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, email: str, username: str) -> User:
        user = User(email=email, username=username)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_username(self, user: User, new_username: str) -> User:
        user.username = new_username
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar(self, user: User, new_avatar: str) -> User:
        user.avatar = new_avatar
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_last_active(self, user: User) -> None:
        user.last_active_at = datetime.now(timezone.utc)
        await self.db.commit()
