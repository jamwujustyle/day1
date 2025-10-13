from fastapi import Depends, Request, UploadFile, File, Form, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import PlainTextResponse

from sqlalchemy.ext.asyncio import AsyncSession

from .services.video import VideoService
from .services.subtitle import SubtitleService
from .schemas.video import VideoResponse

from ..users.services import get_current_user
from ..users.models import User
from ..configs.database import get_db

from uuid import UUID


router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = VideoService(db)
    return await service.upload_video(
        user=current_user,
        file=file,
    )


@router.get("/my-videos", response_model=list[VideoResponse])
async def get_my_videos(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = VideoService(db)

    return await service.get_user_videos(current_user.id)


@router.get("/user/{user_id}/videos", response_model=list[VideoResponse])
async def get_user_videos(user_id: UUID, db: AsyncSession = Depends(get_db)):
    service = VideoService(db)
    return await service.get_user_videos(user_id)


@router.get("/subtitles/{subtitle_id}", response_class=PlainTextResponse)
async def get_subtitle_vtt(subtitle_id: UUID, db: AsyncSession = Depends(get_db)):
    service = SubtitleService(db)
    vtt_content = await service.get_subtitle_as_vtt(subtitle_id)
    if not vtt_content:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return vtt_content
