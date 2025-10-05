from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import AsyncGenerator
from decouple import config

DATABASE_URL = config("DATABASE_URL", None)


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
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
