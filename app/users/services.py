import os
import shutil
import uuid
from typing import List, Optional

from fastapi import Depends, HTTPException, status, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession


from ..users.repository import UserRepository
from ..users.models import User
from ..logs.repositories import UserBioRepository, LogRepository
from ..configs.dependencies import get_current_user
from .schemas import (
    UserLogsSimpleResponse,
    ExtendedLogResponse,
    LocalizationDetail,
    SubtitleInfo,
)


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.bio_repo = UserBioRepository(db)

    async def update_avatar(self, user: User, avatar: UploadFile) -> User:
        AVATAR_MEDIA_ROOT = "media/images/avatars"
        os.makedirs(AVATAR_MEDIA_ROOT, exist_ok=True)

        file_extension = avatar.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(AVATAR_MEDIA_ROOT, unique_filename)
        file_url = f"/{file_path}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        return await self.user_repo.update_avatar(user, file_url)

    async def update_username(self, user: User, new_username: str) -> User:
        return await self.user_repo.update_username(user, new_username)

    async def get_user_profile(self, username: str):
        user = await self.user_repo.get_user_profile(username)
        bio = await self.bio_repo.fetch_user_bio(user.id)

        return {**user.__dict__, "bio": bio}


class UserLogsService:
    def __init__(self, db: AsyncSession):
        self.repo = LogRepository(db)

    async def fetch_user_logs(self, username: str):
        logs = await self.repo.fetch_all_user_logs(username)

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

    async def fetch_log_detail(
        self, username: str, log_id: int, language: str = "en"  # Default language
    ) -> Optional[ExtendedLogResponse]:
        log = await self.repo.fetch_log_by_id(username, log_id, language)

        if not log:
            return None

        video = log.video
        file_url = video.file_url if video else ""

    async def fetch_log_detail(
        self, username: str, log_id: int, language: str = "en"  # Default language
    ) -> Optional[ExtendedLogResponse]:
        """
        Fetch extended log data with language-specific localization.

        Args:
            username: User's username
            log_id: Log ID to fetch
            language: ISO language code (e.g., 'en', 'uz', 'ru')
        """
        log = await self.repo.fetch_log_by_id(username, log_id, language)

        if not log:
            return None

        # Extract video data
        video = log.video
        file_url = video.file_url if video else ""

        # Language mapping (handles both ISO codes and full names)
        lang_map = {
            "en": "english",
            "ru": "russian",
            "ar": "arabic",
            "es": "spanish",
            "zh": "mandarin",
            "fr": "french",
            "hi": "hindi",
            "pt": "portuguese",
            "uz": "uzbek",
        }
        normalize_lang = lambda lang: lang_map.get(lang.lower(), lang.lower())

        requested_lang_normalized = normalize_lang(language)

        # Find localization for requested language
        localization = None
        if video and video.localizations:
            # Try to find exact language match
            for loc in video.localizations:
                if normalize_lang(loc.language) == requested_lang_normalized:
                    localization = LocalizationDetail(
                        language=loc.language, title=loc.title, summary=loc.summary
                    )
                    break

            # Fallback to first available if requested language not found
            if not localization and video.localizations:
                first_loc = video.localizations[0]
                localization = LocalizationDetail(
                    language=first_loc.language,
                    title=first_loc.title,
                    summary=first_loc.summary,
                )

        # Get available subtitles (lightweight - just metadata)
        available_subtitles = []
        current_subtitle_id = None

        if video and video.subtitles:
            for subtitle in video.subtitles:
                available_subtitles.append(
                    SubtitleInfo(id=subtitle.id, language=subtitle.language)
                )
                # Mark current subtitle for requested language
                if normalize_lang(subtitle.language) == requested_lang_normalized:
                    current_subtitle_id = subtitle.id

        # Get thread name
        thread_name = log.thread.name if log.thread else None

        return ExtendedLogResponse(
            log_id=log.id,
            video_id=log.video_id,
            file_url=file_url,
            thread_name=thread_name,
            compressed_context=log.compressed_context,
            localization=localization,
            available_subtitles=available_subtitles,
            current_subtitle_id=current_subtitle_id,
        )
