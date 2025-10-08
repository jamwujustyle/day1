from fastapi import APIRouter, Depends, Request, UploadFile, File

from .services import get_current_user, update_avatar, update_username
from .schemas import UserResponse
from .models import User

from ..configs.database import get_db, AsyncSession

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_current_user_info(
    request: Request, current_user: User = Depends(get_current_user)
):
    # The dependency now implicitly uses the request, but we must accept it in the path function
    # to make it available to the dependency injection system.
    return UserResponse.model_validate(current_user)


@router.get("/profile/{username}")
async def get_user_profile(username: str):
    """
    Get public user profile by username.
    This endpoint doesn't require authentication.
    """
    # TODO: Implement user lookup by username
    return {"message": f"Profile for {username}"}


@router.patch("/image/update")
async def update_user_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated_user = await update_avatar(current_user, file, db)
    return {"id": str(updated_user.id), "avatar": updated_user.avatar}


@router.patch("/username/update")
async def update_user_username(
    request: Request,
    new_username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated_user = await update_username(current_user, new_username, db)

    return {"id": str(updated_user.id), "username": updated_user.username}
