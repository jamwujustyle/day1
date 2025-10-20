from uuid import UUID
from typing import Optional, List, Dict, Any
from ..models import Thread

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class ThreadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_thread(
        self,
        name: str,
        summary: str,
        user_id: UUID,
        keywords: Optional[List[str]],
    ) -> Thread:
        thread = Thread(
            name=name,
            summary=summary,
            user_id=user_id,
            keywords=keywords or None,
        )

        self.db.add(thread)
        await self.db.commit()
        await self.db.refresh(thread)

        return thread

    async def fetch_all_user_threads(self, user_id: UUID) -> List[Thread]:
        threads = await self.db.execute(
            select(Thread).where(Thread.user_id == user_id).order_by()
        )

        return threads.scalars().all()

    async def fetch_all_user_thread_metadata(
        self, user_id: UUID
    ) -> List[Dict[str, Any]]:
        metadata = await self.db.execute(
            select(Thread.id, Thread.name, Thread.summary, Thread.keywords).where(
                Thread.user_id == user_id
            )
        )

        return [
            {"id": id, "name": name, "summary": summary, "keywords": keywords}
            for id, name, summary, keywords in metadata.all()
        ]

    async def update_thread_metadata(
        self, thread_id: UUID, summary: str, keywords: List[str]
    ) -> Optional[Thread]:
        thread = await self.db.get(Thread, thread_id)
        if thread:
            thread.summary = summary
            thread.keywords = keywords
            await self.db.commit()
            await self.db.refresh(thread)
        return thread
