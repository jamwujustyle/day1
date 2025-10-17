from celery import shared_task

from app.users.services import UserService
from app.logs.services import UserContextService
from app.configs.database import AsyncSessionLocal


@shared_task
def update_users_context():

    async def process_active_users():
        async with AsyncSessionLocal() as session:
            user_service = UserService(session)
            context_service = UserContextService(session)

            active_user_ids = await user_service.fetch_active_users()

            if not active_user_ids:
                return

            context_to_update = context_service(active_user_ids)
