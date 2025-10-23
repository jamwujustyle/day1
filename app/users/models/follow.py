from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.sql import func

from app.configs.database import Base
from app.core.mixins import UUIDMixin

from uuid import UUID
from datetime import datetime


class Follow(Base, UUIDMixin):
    __tablename__ = "follows"

    follower_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    following_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
