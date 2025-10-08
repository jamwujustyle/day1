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
    localized_versions: Mapped[List["LocalizedVideo"]] = relationship(
        "LocalizedVideo", back_populates="video", cascade="all, delete-orphan"
    )


class LocalizedVideo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "localized_videos"

    language: Mapped[str] = mapped_column(nullable=False)
    file_url: Mapped[str] = mapped_column(nullable=False)

    video_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False
    )
    video: Mapped["Video"] = relationship("Video", back_populates="localized_versions")
