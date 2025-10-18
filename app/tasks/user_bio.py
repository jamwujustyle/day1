from celery import shared_task

from app.logs.services import UserBioService
from app.logs.services import ThreadService
from app.logs.schemas import UserBioAIResponse
from app.configs.database import AsyncSessionLocal

from uuid import UUID
import json
import asyncio

from app.configs.logging_config import logger


@shared_task
def update_user_bio(user_id: str):

    async def process_active_users():
        async with AsyncSessionLocal() as session:
            thread_service = ThreadService(session)
            bio_service = UserBioService(session)

            user_threads = await thread_service.fetch_all_user_thread_metadata(
                UUID(user_id)
            )

            if not user_threads:
                logger.critical("no threads found")
                return

            existing_user_bio = await bio_service.fetch_user_bio(UUID(user_id))

            existing_bio_text = (
                existing_user_bio
                if existing_user_bio
                else "None - This is the first analysis for the user"
            )

            from . import make_request, USER_BIO_PROMPT

            prompt = USER_BIO_PROMPT.format(
                existing_bio=existing_bio_text,
                threads_metadata=json.dumps(user_threads, indent=2, default=str),
            )

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes user behaviour patterns and generated bio summaries in JSON format.",
                },
                {"role": "user", "content": prompt},
            ]

            result = make_request(
                messages=messages, prompt_cache_key="user_bio_analysis"
            )
            response_data = UserBioAIResponse(**result)

            updated_bio = response_data.bio

            await bio_service.get_or_create_bio(user_id=UUID(user_id), bio=updated_bio)

    asyncio.run(process_active_users())
