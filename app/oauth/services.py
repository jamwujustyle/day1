import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from ..configs.jwt import create_access_token, create_refresh_token
from ..users.repository import UserRepository
from .repository import SocialAccountRepository
from .provider import GoogleProvider


class OAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.social_repo = SocialAccountRepository(db)
        self.provider = GoogleProvider()

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        token_data = self.provider.get_token_data(code, redirect_uri)

        async with httpx.AsyncClient() as client:
            response = await client.post(self.provider.token_url, data=token_data)
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.provider.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            response.raise_for_status()
            return response.json()

    async def authenticate_or_create_user(self, google_user_data: dict):
        email = google_user_data["email"]

        social_account = await self.social_repo.get_by_email(email)

        if social_account:
            await self.social_repo.update_provider_data(
                social_account.id, google_user_data
            )
            user = await self.user_repo.get_by_id(social_account.user_id)

            return user, False

        user = await self.user_repo.get_by_email(email)

        if user:
            await self.social_repo.create(
                user_id=user.id,
                email=email,
                provider_data=google_user_data,
            )
            return user, False

        user = await self.user_repo.create(email=email)

        await self.social_repo.create(
            user_id=user.id, email=email, provider_data=google_user_data
        )

        return user, True

    async def handle_oauth_callback(self, code: str, redirect_uri: str):
        token_response = await self.exchange_code_for_token(code, redirect_uri)

        access_token = token_response["access_token"]

        google_user_data = await self.get_user_info(access_token)

        user, is_new = await self.authenticate_or_create_user(google_user_data)

        access_token = create_access_token(user.id, user.email)
        refresh_token = create_refresh_token(user.id)

        return {
            "user": user,
            "is_new_user": is_new,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
