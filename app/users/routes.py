from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
    File,
    Query,
    HTTPException,
    status,
)


from .services import UserService, UserLogsService
from .schemas import (
    UserResponse,
    UpdateUsernameRequest,
    UserLogsListResponse,
    ExtendedLogResponse,
)
from .models import User

from ..configs.database import get_db, AsyncSession
from ..configs.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_current_user_info(
    request: Request, current_user: User = Depends(get_current_user)
):
    return UserResponse.model_validate(current_user)


@router.get("/profile/{username}")
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_profile(username)
    return UserResponse.model_validate(user)


@router.patch("/avatar/update")
async def update_user_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    updated_user = await service.update_avatar(current_user, avatar)
    return {"id": str(updated_user.id), "avatar": updated_user.avatar}


@router.patch("/username/update")
async def update_user_username(
    payload: UpdateUsernameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)

    updated_user = await service.update_username(current_user, payload.new_username)

    return {"id": str(updated_user.id), "username": updated_user.username}


@router.get("/{username}/logs", response_model=UserLogsListResponse)
async def list_user_logs(username: str, db: AsyncSession = Depends(get_db)):
    user_service = UserLogsService(db)
    logs = await user_service.fetch_user_logs(username)

    return UserLogsListResponse(logs=logs)


@router.get("/{username}/logs/{log_id}", response_model=ExtendedLogResponse)
async def retrieve_user_log(
    username: str,
    log_id: int,
    language: str = Query(
        default="en", description="language code for localization", regex="^[a-z]{2}$"
    ),
    db: AsyncSession = Depends(get_db),
):
    # query params:
    # - lang: ISO 639-1 code default en

    user_service = UserLogsService(db)
    log_detail = await user_service.fetch_log_detail(
        username=username, log_id=log_id, language=language
    )

    if not log_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="resource not found"
        )
    return log_detail
