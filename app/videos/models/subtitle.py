from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey, Text, JSON

from app.core.mixins import UUIDMixin, TimestampMixin
from app.configs.database import Base

from uuid import UUID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Video


class Subtitle(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subtitles"

    language: Mapped[str] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    segments: Mapped[dict] = mapped_column(JSON, nullable=True)

    video_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False, index=True
    )
    video: Mapped["Video"] = relationship("Video", back_populates="subtitles")
