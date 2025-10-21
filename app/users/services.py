import os
import shutil
import uuid
from typing import List

from fastapi import Depends, HTTPException, status, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession


from ..users.repository import UserRepository
from ..users.models import User
from ..logs.services import UserBioService
from ..configs.dependencies import get_current_user


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.bio_repo = UserBioService(db)

    async def get_optional_user(
        self,
        request: Request,
    ) -> User | None:
        try:
            return await get_current_user(request, self.user_repo.db)
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
        return await self.user_repo.update_avatar(user, file_url)

    async def update_username(self, user: User, new_username: str) -> User:
        return await self.user_repo.update_username(user, new_username)

    async def get_user_profile(self, username: str):
        user = await self.user_repo.get_user_profile(username)
        bio = await self.bio_repo.fetch_user_bio(user.id)

        return {**user.__dict__, "bio": bio}

    async def fetch_active_users(self) -> List[uuid.UUID]:
        return await self.user_repo.fetch_active_users()
