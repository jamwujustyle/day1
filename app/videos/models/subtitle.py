from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey

from app.core.mixins import UUIDMixin, TimestampMixin
from app.configs.database import Base

from uuid import UUID


class Subtitle(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subtitles"

    language: Mapped[str] = mapped_column(nullable=False)
    file_url: Mapped[str] = mapped_column(nullable=False)

    video_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False
    )
    video: Mapped["Video"] = relationship("Video", back_populates="subtitles")
