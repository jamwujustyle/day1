from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Text
from uuid import UUID
from typing import Optional, TYPE_CHECKING

from app.core.mixins import TimestampMixin, UUIDMixin
from app.configs.database import Base

if TYPE_CHECKING:
    from app.users.models import User
    from app.videos.models import Video
    from . import Thread


class Log(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "logs"

    compressed_context: Mapped[str] = mapped_column(Text, nullable=False)

    # relations
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    video_id: Mapped[UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    thread_id: Mapped[UUID] = mapped_column(
        ForeignKey("threads.id", ondelete="CASCADE"), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="logs")
    video: Mapped["Video"] = relationship(back_populates="log")
    thread: Mapped[Optional["Thread"]] = relationship(back_populates="logs")
