from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey
from uuid import UUID
from typing import List

from ...core.mixins import UUIDMixin, TimestampMixin
from ...configs.database import Base


class Video(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "videos"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    file_url: Mapped[str] = mapped_column(nullable=False)

    # RELATIONS
    user: Mapped["User"] = relationship("User", back_populates="videos")

    subtitles: Mapped[List["Subtitle"]] = relationship(
        "Subtitle", back_populates="video", cascade="all, delete-orphan"
    )
    audios: Mapped[List["Audio"]] = relationship(
        "Audio", back_populates="video", cascade="all, delete-orphan"
    )
