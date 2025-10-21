from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path


from .oauth.routes import router as oauth_router
from .auth.routes import router as auth_router
from .users.routes import router as user_router
from .videos.routes import router as video_router

# Import all models to ensure SQLAlchemy mapper registry is populated
from .logs.models import Log, Thread, UserBio
from .videos.models import Video, VideoLocalization, Subtitle
from .users.models import User
from .auth.models import MagicLink
from .oauth.models import SocialAccount


from .middlewares import register_datetime_middleware
from .configs.settings import get_settings

settings = get_settings()

app = FastAPI(title="logg", version="1.0.0")

app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name="media")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
)
# app.add_middleware(LastActiveMiddleware)


@app.get("/oauth-test")
async def get_user_test_page():
    return FileResponse("app/oauth.html")


@app.get("/video-test")
async def get_video_test_page():
    return FileResponse("app/video.html")


@app.get("/user-test")
async def get_user_test_page():
    return FileResponse("app/users.html")


@app.get("/passwordless-test")
async def get_passwordless_test_page():
    return FileResponse("app/passwordless.html")


app.include_router(oauth_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(video_router)
