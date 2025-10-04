import secrets
from typing import Dict
from decouple import config

from fastapi import Request
from fastapi.routing import APIRouter

from urllib.parse import urlencode

router = APIRouter()


class GoogleProvider:
    name = "google"
    display_name = "Google"
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    scope = "openid email profile"

    def get_client_id(self) -> str:
        return config("GOOGLE_CLIENT_ID", None)

    def get_client_secret(self) -> str:
        return config("GOOGLE_CLIENT_SECRET")

    def get_redirect_url(self, request: Request) -> str:
        return request.url_for("oauth_callback", provider=self.name)

    def get_auth_params(self, redirect_uri: str, state: str) -> Dict[str, str]:
        return {
            "client_id": self.get_client_id(),
            "redirect_uri": redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": state,
        }

    def build_auth_url(self, request) -> str:
        redirect_uri = self.get_redirect_url(request)
        state = secrets.token_urlsafe(16)
        params = self.get_auth_params(redirect_uri, state)

        request.session["oauth_state"] = state

        return f"{self.auth_url}?{urlencode(params)}"

    def get_token_data(self, code: str, redirect_uri: str) -> dict:
        return {
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret(),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

    def normalize_user_data(self, raw_data: dict) -> dict:
        return {
            "id": raw_data["id"],
            "email": raw_data["email"],
            "avatar": raw_data.get("picture", None),
            "email_verified": raw_data.get("verified_email", False),
        }
