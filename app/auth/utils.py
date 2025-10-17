from fastapi.responses import Response
from ..configs.jwt import ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE
from ..configs.settings import get_settings
import resend

settings = get_settings()


def set_auth_cookies(response: Response, tokens: dict) -> Response:
    # TODO: CHANGE IN PROD
    response.set_cookie(
        "access_token",
        value=tokens["access_token"],
        max_age=ACCESS_TOKEN_EXPIRE * 60,
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        value=tokens["refresh_token"],
        max_age=REFRESH_TOKEN_EXPIRE * 24 * 60 * 60,
        httponly=True,
        secure=settings.SECURE_COOKIES,  # Set to True in production
        samesite="lax",
        path="/",
    )

    return response


def clear_auth_cookies(response: Response) -> Response:

    response.delete_cookie(
        "access_token",
        path="/",
        secure=settings.SECURE_COOKIES,
        samesite="lax",
    )

    response.delete_cookie(
        "refresh_token",
        path="/",
        secure=settings.SECURE_COOKIES,
        samesite="lax",
    )

    return response


async def send_auth_code_email(email, magic_link_url, otp_code):
    try:
        context = {
            "magic_link_url": magic_link_url,
            "otp_code": otp_code,
            "site_name": "logg.gg",
        }

        subject = f"Your authentication code for {context['site_name']}"
        html_content = f"""
            <p>Your verification code: <b>{otp_code}</b></p>
            <p>Or click the link below to sign in:</p>
            <a href="{magic_link_url}">{magic_link_url}</a>
        """
        resend.api_key = settings.RESEND_API_KEY

        resend.Emails.send(
            {
                "from": settings.FROM_EMAIL,
                "to": email,
                "subject": subject,
                "html": html_content,
            }
        )
    except Exception as ex:
        print(f"❌ Email send failed: {ex}")
        return False
