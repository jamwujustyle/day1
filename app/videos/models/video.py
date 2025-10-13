from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey, String, Text
from uuid import UUID
from typing import List, TYPE_CHECKING

from ...core.mixins import UUIDMixin, TimestampMixin
from ...configs.database import Base

if TYPE_CHECKING:
    from ...users.models import User
    from .subtitle import Subtitle


class Video(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "videos"

    source_language: Mapped[str] = mapped_column(String, nullable=True)

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    file_url: Mapped[str] = mapped_column(nullable=False)

    # RELATIONS
    user: Mapped["User"] = relationship("User", back_populates="videos")

    subtitles: Mapped[List["Subtitle"]] = relationship(
        "Subtitle", back_populates="video", cascade="all, delete-orphan"
    )
    localizations: Mapped[List["VideoLocalization"]] = relationship(
        "VideoLocalization", back_populates="video", cascade="all, delete-orphan"
    )


class VideoLocalization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "video_localizations"

    video_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE")
    )
    video: Mapped["Video"] = relationship("Video", back_populates="localizations")
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(String(70), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
