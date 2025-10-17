from celery import shared_task

from app.users.services import UserService
from app.logs.services import UserContextService
from app.configs.database import AsyncSessionLocal


@shared_task
def update_users_context():

    async def process_active_users():
        async with AsyncSessionLocal() as session:
            user_service = UserService(session)
            active_users = await user_service.fetch_active_users()

            if not active_users:
                return

            try: