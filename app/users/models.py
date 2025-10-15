from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship


from ..configs.database import Base
from ..core.mixins import UUIDMixin

if TYPE_CHECKING:
    from ..videos.models import Video
    from ..logs.models import Log
    from ..logs.models import Project
    from ..logs.models import UserContext


class User(Base, UUIDMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    last_login: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=True
    )
    last_active_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
    )

    social_accounts = relationship(
        "SocialAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    videos: Mapped[list["Video"]] = relationship(
        "Video", back_populates="user", cascade="all, delete-orphan"
    )
    logs: Mapped[list["Log"]] = relationship(
        "Log", back_populates="user", cascade="all, delete-orphan"
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )
    user_contexts: Mapped[list["UserContext"]] = relationship(
        "UserContext", back_populates="user", cascade="all, delete-orphan"
    )
