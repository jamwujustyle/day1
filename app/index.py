from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.sessions import SessionMiddleware
from decouple import config
from pathlib import Path


from .oauth.routes import router as oauth_router
from .users.routes import router as user_router
from .videos.routes import router as video_router

app = FastAPI(title="logg", version="1.0.0")

MEDIA_ROOT = Path(config("MEDIA_ROOT"))
MEDIA_URL = config("MEDIA_URL")

app.mount(MEDIA_URL, StaticFiles(directory=MEDIA_ROOT), name="media")


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
    secret_key=config("SESSION_SECRET"),
)


app.include_router(oauth_router)
app.include_router(user_router)
app.include_router(video_router)
