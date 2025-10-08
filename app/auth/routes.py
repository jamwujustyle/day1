from fastapi.routing import APIRouter
from fastapi import Response, Request, Depends

from .services import refresh_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token", httponly=True, secure=False, samesite="lax"
    )

    response.delete_cookie(
        key="refresh_token", httponly=True, secure=False, samesite="lax"
    )

    return {"message": "Logout successful. Tokens have been cleared"}


@router.post("/refresh")
async def refresh_token_endpoint(
    response: Response, request: Request, result: dict = Depends(refresh_access_token)
):
    return result
