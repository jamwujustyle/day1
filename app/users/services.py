import os
import shutil
import uuid
from typing import List

from fastapi import Depends, HTTPException, status, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession


from ..users.repository import UserRepository
from ..users.models import User
from ..logs.repositories import UserBioRepository, LogRepository
from ..configs.dependencies import get_current_user
from .schemas import (
    UserLogsSimpleResponse,
)


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.bio_repo = UserBioRepository(db)
        self.log_repo = LogRepository(db)

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

    async def fetch_user_logs(self, username: str):
        logs = await self.log_repo.fetch_all_user_logs(username)

        response_logs = []
        for log in logs:
            # Safely build video response, avoid lazy loads by using eager-loaded relationships
            title = ""
            summary = None
            if getattr(log, "video", None) and log.video.localizations:
                first_loc = log.video.localizations[0]
                title = (first_loc.title or "") if hasattr(first_loc, "title") else ""
                summary = getattr(first_loc, "summary", None)

            thread_name = log.thread.name if getattr(log, "thread", None) else None
            title
            response_logs.append(
                UserLogsSimpleResponse(
                    log_id=log.id, title=title, summary=summary, thread_name=thread_name
                )
            )

        return response_logs
