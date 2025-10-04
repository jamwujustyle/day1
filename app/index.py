from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from decouple import config

app = FastAPI(title="logg", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=config("SESSION_SECRET"),
)

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def debug():
    return {"message": "hello world"}


app.include_router(router)
