from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Datetime, Boolean

from app.core.mixins import TimestampMixin, UUIDMixin
from app.configs.database import Base

from datetime import datetime, timezone


class MagicLink(Base, TimestampMixin, UUIDMixin):
    __tablename__ = "magic_links"

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=False)
    otp: Mapped[str] = mapped_column(String(6), default="000000")
    expires_at: Mapped[datetime] = mapped_column(Datetime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def is_expired(self):
        return datetime.now(timezone.utc) > self.expires_at

    async def use(self, db_session):
        self.used = True
        db_session.add(self)
        await db_session.commit()
        await db_session.refresh(self)
