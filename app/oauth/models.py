import uuid

from ..configs.database import Base
from ..core.mixins import UUIDMixin

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship


class SocialAccount(Base, UUIDMixin):
    __tablename__ = "social_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    provider_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    user = relationship("User", back_populates="social_accounts")
