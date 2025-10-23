# from typing import Optional, TYPE_CHECKING
# from datetime import datetime, timezone
# from sqlalchemy import String, TIMESTAMP
# from sqlalchemy.orm import Mapped, mapped_column, relationship


# from ..configs.database import Base
# from ..core.mixins import UUIDMixin

# if TYPE_CHECKING:
#     from app.videos.models import Video
#     from app.logs.models import Log, Thread, UserBio


# class User(Base, UUIDMixin):
#     __tablename__ = "users"

#     username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
#     avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
#     email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

#     created_at: Mapped[datetime] = mapped_column(
#         TIMESTAMP(timezone=True),
#         default=datetime.now(timezone.utc),
#         nullable=False,
#     )

#     social_accounts = relationship(
#         "SocialAccount",
#         back_populates="user",
#         cascade="all, delete-orphan",
#         uselist=False,
#     )
#     videos: Mapped[list["Video"]] = relationship(
#         "Video", back_populates="user", cascade="all, delete-orphan"
#     )
#     logs: Mapped[list["Log"]] = relationship(
#         "Log", back_populates="user", cascade="all, delete-orphan"
#     )
#     threads: Mapped[list["Thread"]] = relationship(
#         "Thread", back_populates="user", cascade="all, delete-orphan"
#     )
#     user_bios: Mapped[list["UserBio"]] = relationship(
#         "UserBio", back_populates="user", cascade="all, delete-orphan"
#     )
