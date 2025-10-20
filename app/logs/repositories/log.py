from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Log
from uuid import UUID


class LogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(
        self,
        compressed_context: str,
        user_id: UUID,
        video_id: UUID,
        # thread_id: UUID = None,
    ) -> Log:
        log = Log(
            compressed_context=compressed_context,
            user_id=user_id,
            video_id=video_id,
            # thread_id=thread_id,
        )

        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)

        return log

    async def link_log_to_thread(self, log_id: UUID, thread_id: UUID):
        log = await self.db.get(Log, log_id)
        if log:
            log.thread_id = thread_id
            await self.db.commit()
            await self.db.refresh(log)
        return log
