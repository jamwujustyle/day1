from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine as create_sync_engine
from typing import AsyncGenerator
from sqlalchemy.pool import NullPool
from .settings import get_settings

settings = get_settings()

DATABASE_URL = settings.DATABASE_URL

sync_engine = create_sync_engine(
    DATABASE_URL.replace("+asyncpg", ""), echo=False, pool_size=5
)

SyncSessionLocal = sessionmaker(bind=sync_engine)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,
)


AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase): ...


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
