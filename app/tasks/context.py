from celery import shared_task

from app.users.services import UserService
from app.logs.services import UserContextService
from app.configs.database import AsyncSessionLocal


@shared_task
def update_users_context():
    async_db = AsyncSessionLocal()

    user_service = UserService(async_db)
