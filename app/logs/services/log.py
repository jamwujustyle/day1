from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories import LogRepository
from uuid import UUID


class LogService:
    def __init__(self, db: AsyncSession):
        self.repo = LogRepository(db)

    async def create_log(self, compressed_context, user_id, video_id):

        return await self.repo.create_log(
            compressed_context=compressed_context,
            user_id=user_id,
            video_id=video_id,
            # thread_id=thread_id,
        )

    async def link_log_to_thread(self, log_id: UUID, thread_id: UUID):
        log = await self.repo.link_log_to_thread(log_id=log_id, thread_id=thread_id)

        return log
