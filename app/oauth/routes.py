from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..configs.database import get_db

from .provider import GoogleProvider
from .services import OAuthService
from .schemas import OAuthCallbackResponse

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/google")
async def google_login(request: Request):
    auth_url = GoogleProvider().build_auth_url(request)
    return RedirectResponse(auth_url)


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    request: Request,
    response: Response,
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

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        # TODO: CHANGE IN PROD
        secure=False,
        samesite="lax",
        max_age=1800,
    )
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800,
    )

    return OAuthCallbackResponse(user=user, is_new_user=result["is_new_user"])
