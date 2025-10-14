from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DEBUG: bool
    SESSION_SECRET: str
    JWT_SECRET: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    DATABASE_URL: str

    MEDIA_ROOT: str
    MEDIA_URL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    OPENAI_API_KEY: str
    ELEVENLABS_API_KEY: str
    RESEND_API_KEY: str

    FRONTEND_URL: str
    FROM_EMAIL: str = "onboarding@resend.dev"

    @property
    def SECURE_COOKIES(self) -> bool:
        return not self.DEBUG

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
