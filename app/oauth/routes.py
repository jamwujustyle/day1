from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..configs.database import get_db
from ..configs.jwt import (
    verify_refresh_token,
    create_access_token,
    create_refresh_token,
)
from ..users.repository import UserRepository
from .provider import GoogleProvider
from .services import OAuthService

router = APIRouter(prefix="/auth", tags=["oauth"])


@router.get("/google")
async def google_login(request: Request):
    auth_url = GoogleProvider().build_auth_url(request)
    return RedirectResponse(auth_url)


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    request: Request,
    code: str = None,
    state: str = None,
    db: AsyncSession = Depends(get_db),
):
    if provider != "google":
        raise HTTPException(status_code=400, detail="Invalid provider")

    stored_state = request.session.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=401, detail="Invalid state parameter")

    request.session.pop("oauth_state", None)

    if not code:
        raise HTTPException(status_code=401, detail="No authorization code provided")

    redirect_uri = GoogleProvider().get_redirect_url(request)

    oauth_service = OAuthService(db)
    result = await oauth_service.handle_oauth_callback(code, redirect_uri)

    user = result["user"]

    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": result["token_type"],
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at.isoformat(),
        },
        "is_new_user": result["is_new_user"],
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint - with JWT auth, logout is handled client-side.
    Client should delete the JWT token from storage.

    For true server-side logout, you would need to implement:
    - Token blacklist/revocation
    - Store invalidated tokens in Redis with TTL
    """
    return {
        "message": "Logout successful. Client should delete JWT token.",
        "action": "delete_token_client_side",
    }
