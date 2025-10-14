from fastapi.responses import Response
from ..configs.jwt import ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE

from decouple import config

SECURE_COOKIES = config("SECURE_COOKIES", default=False, cast=bool)


def set_auth_cookies(response: Response, tokens: dict) -> Response:
    # TODO: CHANGE IN PROD
    response.set_cookie(
        "access_token",
        value=tokens["access_token"],
        max_age=ACCESS_TOKEN_EXPIRE * 60,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        value=tokens["refresh_token"],
        max_age=REFRESH_TOKEN_EXPIRE * 24 * 60 * 60,
        httponly=True,
        secure=SECURE_COOKIES,  # Set to True in production
        samesite="lax",
        path="/",
    )

    return response


def clear_auth_cookies(response: Response) -> Response:

    response.delete_cookie(
        "access_token",
        path="/",
        secure=SECURE_COOKIES,
        samesite="lax",
    )

    response.delete_cookie(
        "refresh_token",
        path="/",
        secure=SECURE_COOKIES,
        samesite="lax",
    )

    return response
