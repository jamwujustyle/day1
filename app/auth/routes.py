from fastapi.routing import APIRouter
from fastapi import Response, Request, Depends

from .services import refresh_access_token
from .utils import clear_auth_cookies

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
