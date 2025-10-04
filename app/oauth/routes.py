from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..configs.database import get_db
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

    request.session.pop("oauth_session", None)
