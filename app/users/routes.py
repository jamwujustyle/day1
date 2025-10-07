from fastapi import APIRouter, Depends

from .services import get_current_user, update_avatar
from ..configs.database import get_db, AsyncSession
from .models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):

    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat(),
    }


@router.get("/profile/{username}")
async def get_user_profile(username: str):
    """
    Get public user profile by username.
    This endpoint doesn't require authentication.
    """
    # TODO: Implement user lookup by username
    return {"message": f"Profile for {username}"}


@router.patch("/image/update/")
async def update_user_avatar(
    new_avatar: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated_user = await update_avatar(current_user, new_avatar, db)
    return {"id": str(updated_user.id), "avatar": updated_user.avatar}
