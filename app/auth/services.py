import uuid, secrets
from datetime import datetime, timezone, timedelta
from fastapi import Request, Response, HTTPException, status, Depends
from fastapi.exceptions import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from ..configs.jwt import (
    verify_refresh_token,
    create_access_token,
    create_refresh_token,
)
from ..users.repository import UserRepository
from ..configs.database import get_db
from .utils import set_auth_cookies, send_auth_code_email
from .repository import PasswordlessRepository
from app.configs.settings import get_settings

settings = get_settings()


class PasswordlessService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.repo = PasswordlessRepository(db)

    async def request_magic_link(self, email: str):
        token = secrets.token_urlsafe(32)
        otp = "".join(str(secrets.randbelow(10)) for _ in range(6))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        await self.repo.create_magic_link(
            email=email, otp=otp, token=token, expires_at=expires_at
        )
        # TODO: ADJUST URL
        magic_link_url = f"{settings.FRONTEND_URL}/auth/verify/{token}"

        await send_auth_code_email(
            email=email, magic_link_url=magic_link_url, otp_code=otp
        )

    async def verify_magic_link(self, token):
        link = await self.repo.get_magic_link_by_token(token)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired magic link",
            )
        if link.used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The magic link has already been used",
            )
        if link.is_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The magic link has expired",
            )

        user = await self.repo.get_or_create_user(link.email)

        await link.use(self.repo.db)

        return user

    async def verify_otp(self, email: str, otp_code: str):
        link = await self.repo.get_magic_link_by_email_and_otp(
            email=email, otp_code=otp_code
        )

        if not link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP code",
            )
        if link.is_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This OTP code has expired. Please request a new one",
            )

        user = await self.repo.get_or_create_user(link.email)
        await link.use(self.repo.db)

        return user


async def refresh_access_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )

    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(uuid.UUID(user_id_str))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = create_access_token(user.id, user.email)
    new_refresh_token = create_refresh_token(user.id)

    tokens = {"access_token": new_access_token, "refresh_token": new_refresh_token}

    set_auth_cookies(response, tokens)

    return {"message": "Tokens refreshed successfully"}
