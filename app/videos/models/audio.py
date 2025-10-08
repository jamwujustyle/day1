from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey

from uuid import UUID

from app.core.mixins import UUIDMixin, TimestampMixin
from app.configs.database import Base


class Audio(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audios"

    language: Mapped[str] = mapped_column(nullable=False)
    file_url: Mapped[str] = mapped_column(nullable=False)

    video_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False
    )
    video: Mapped["Video"] = relationship("Video", back_populates="audios")
