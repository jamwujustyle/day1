from fastapi import APIRouter, Depends, Request, UploadFile, File


from .services import UserService
from .schemas import UserResponse
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


@router.patch("/image/update")
async def update_user_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    updated_user = await service.update_avatar(current_user, file, db)
    return {"id": str(updated_user.id), "avatar": updated_user.avatar}


@router.patch("/username/update")
async def update_user_username(
    request: Request,
    new_username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)

    updated_user = await service.update_username(current_user, new_username, db)

    return {"id": str(updated_user.id), "username": updated_user.username}
