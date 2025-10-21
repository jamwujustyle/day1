from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, load_only
from sqlalchemy import select
from ..models import Log, Thread
from app.videos.models import Video, VideoLocalization
from app.users.models import User
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

    async def fetch_all_user_logs(self, username: str):
        logs = await self.db.execute(
            select(Log)
            .join(Log.user)
            .where(User.username == username)
            .options(
                load_only(Log.id, Log.video_id, Log.thread_id),
                # Eagerly load related entities to avoid async lazy-load (MissingGreenlet)
                selectinload(Log.video).load_only(Video.file_url),
                selectinload(Log.video)
                .selectinload(Video.localizations)
                .load_only(VideoLocalization.title, VideoLocalization.summary),
                selectinload(Log.thread).load_only(Thread.name),
            )
            .order_by(Log.id.desc())
        )
        return logs.scalars().all()

    async def fetch_log_by_id(self, log_id: int):
        log = await self.db.execute(
            select(Log)
            .where(Log.id == log_id)
            .options(
                selectinload(Log.video).load_only(Video.file_url),
                selectinload(Log.video)
                .selectinload(Video.localizations)
                .load_only(VideoLocalization.title, VideoLocalization.summary),
                selectinload(Log.thread).load_only(Thread.name),
            )
        )

        return log.scalar_one_or_none()
