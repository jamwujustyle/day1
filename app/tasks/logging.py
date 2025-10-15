from celery import shared_task
from app.logs.services import LogService
from app.configs.database import AsyncSessionLocal


@shared_task
def create_log():
    async_db = AsyncSessionLocal()
    log_service = LogService(async_db)
