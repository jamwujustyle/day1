from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Text, String, ARRAY
from sqlalchemy.dialects.postgresql import VARCHAR
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING

from app.core.mixins import TimestampMixin, UUIDMixin
from app.configs.database import Base

if TYPE_CHECKING:
    from app.users.models import User
    from . import Log


class Thread(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "threads"
    # TODO: CHANGE LATER
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    keywords: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(VARCHAR(40)), nullable=True
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user: Mapped["User"] = relationship(back_populates="threads")
    logs: Mapped[List["Log"]] = relationship(
        "Log", back_populates="thread", cascade="all, delete-orphan"
    )
