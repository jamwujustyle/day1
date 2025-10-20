from ..repositories import ThreadRepository
from ..models import Thread

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional


class ThreadService:
    def __init__(self, db: AsyncSession):
        self.repo = ThreadRepository(db)

    async def create_thread(
        self, name: str, summary: str, user_id: UUID, keywords: Optional[List[str]]
    ) -> Thread:
        return await self.repo.create_thread(
            name=name, summary=summary, user_id=user_id, keywords=keywords or None
        )

    async def fetch_all_user_threads(self, user_id: UUID):
        return await self.repo.fetch_all_user_threads(user_id)

    async def fetch_all_user_thread_metadata(self, user_id: UUID):
        return await self.repo.fetch_all_user_thread_metadata(user_id)

    async def update_thread_metadata(
        self, thread_id: UUID, summary: str, keywords: List[str]
    ) -> Optional[Thread]:
        return await self.repo.update_thread_metadata(
            thread_id=thread_id, summary=summary, keywords=keywords
        )
