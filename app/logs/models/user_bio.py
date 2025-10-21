from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Text
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING

from app.core.mixins import TimestampMixin, UUIDMixin
from app.configs.database import Base

if TYPE_CHECKING:
    from app.users.models import User


class UserBio(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_bios"

    bio: Mapped[str] = mapped_column(Text)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user: Mapped["User"] = relationship(back_populates="user_bios")
