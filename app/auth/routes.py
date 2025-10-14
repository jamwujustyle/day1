from fastapi.routing import APIRouter
from fastapi import Response, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .services import refresh_access_token, MagicAuthService
from .utils import clear_auth_cookies, set_auth_cookies
from .schemas import AuthCodeRequest, TokenRequest, OTPVerifyRequest

from ..users.schemas import UserResponse
from ..configs.database import get_db
from ..configs.jwt import create_access_token, create_refresh_token

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


@router.post("/verify-magic-link")
async def verify_magic_link(
    payload: TokenRequest, response: Response, db=Depends(get_db)
) -> UserResponse:
    service = MagicAuthService(db)
    user = await service.verify_magic_link(token=payload.token)

    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id)
    tokens = {"access_token": access_token, "refresh_token": refresh_token}

    set_auth_cookies(response, tokens)

    return UserResponse.model_validate(user)


@router.post("/verify-otp")
async def verify_otp(
    payload: OTPVerifyRequest, response: Response, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    service = MagicAuthService(db)
    user = await service.verify_otp(otp_code=payload.otp_code, email=payload.email)

    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id)
    tokens = {"access_token": access_token, "refresh_token": refresh_token}

    set_auth_cookies(response, tokens)

    return UserResponse.model_validate(user)
