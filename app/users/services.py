import os
import shutil
import uuid
from typing import List

from fastapi import Depends, HTTPException, status, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession


from ..configs.database import get_db
from ..users.repository import UserRepository
from ..users.models import User
from ..configs.dependencies import get_current_user


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_optional_user(
        self,
        request: Request,
    ) -> User | None:
        try:
            return await get_current_user(request, self.repo.db)
        except HTTPException:
            return None

    async def update_avatar(self, user: User, file: UploadFile) -> User:
        AVATAR_MEDIA_ROOT = "media/images/avatars"
        os.makedirs(AVATAR_MEDIA_ROOT, exist_ok=True)

        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(AVATAR_MEDIA_ROOT, unique_filename)
        file_url = f"/{file_path}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return await self.repo.update_avatar(user, file_url)

    async def update_username(self, user: User, new_username: str) -> User:
        return await self.repo.update_username(user, new_username)

    async def get_user_by_username(self, username: str):
        return await self.repo.get_user_by_username(username)

    async def fetch_active_users(self) -> List[User]:
        return await self.repo.fetch_active_users()
