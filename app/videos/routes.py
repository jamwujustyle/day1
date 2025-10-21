from fastapi import Depends, Request, UploadFile, File, Form, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import PlainTextResponse

from sqlalchemy.ext.asyncio import AsyncSession

from .services import VideoService
from .services import SubtitleService
from .schemas import VideoUploadResponse, VideoGetResponse

from ..users.services import get_current_user
from ..users.models import User
from ..configs.database import get_db

from uuid import UUID


router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = VideoService(db)
    video = await service.upload_video(
        user=current_user,
        file=file,
    )
    return VideoUploadResponse.model_validate(video)


# TODO: REFINE PREFETCH LOGIC TO FETCH SUBTITLES LOCALIZATIONS TITLES SUMMARIES ONLY ON DEMAND > DEFAULT TO SELECTED LANGUAGE
@router.get("/my-videos", response_model=list[VideoGetResponse])
async def get_my_videos(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = VideoService(db)

    return await service.get_user_videos(current_user.id)


@router.get("/user/{user_id}/logs", response_model=list[VideoGetResponse])
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
