import uuid, secrets, random
from datetime import datetime, timezone, timedelta
from fastapi import Request, Response, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..configs.jwt import (
    verify_refresh_token,
    create_access_token,
    create_refresh_token,
)
from ..users.repository import UserRepository
from ..configs.database import get_db
from .utils import set_auth_cookies
from .repository import MagicAuthRepository


class MagicAuthService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.repo = MagicAuthRepository(db)

    async def request_magic_link(self, email: str):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(10)
        otp = f"{random.randint(0, 999999):06d}"

        await self.repo.create_magic_link(
            email=email, otp=otp, token=token, expires_at=expires_at
        )


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
