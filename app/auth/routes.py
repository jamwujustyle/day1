from fastapi.routing import APIRouter
from fastapi import Response, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .services import refresh_access_token, MagicAuthService
from .utils import clear_auth_cookies
from .schemas import AuthCodeRequest

from ..configs.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"message": "Logout successful. Tokens have been cleared"}


@router.post("/refresh")
async def refresh_token_endpoint(
    response: Response, request: Request, result: dict = Depends(refresh_access_token)
):
    return result


@router.post("/request-code")
async def request_auth_code(
    payload: AuthCodeRequest, db: AsyncSession = Depends(get_db)
):
    service = MagicAuthService(db)
    await service.request_magic_link(email=payload.email)

    return JSONResponse(
        status_code=200, content={"detail": "Magic link and OTP sent to your email"}
    )
