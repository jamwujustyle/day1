from celery import shared_task

from app.logs.services import UserContextService
from app.logs.services import ThreadService
from app.logs.schemas import UserContextAIResponse
from app.configs.database import AsyncSessionLocal

from uuid import UUID
import json
import asyncio

from app.configs.logging_config import logger


@shared_task
def update_user_context(user_id: str):

    async def process_active_users():
        async with AsyncSessionLocal() as session:
            thread_service = ThreadService(session)
            context_service = UserContextService(session)

            user_threads = await thread_service.fetch_all_user_thread_metadata(
                UUID(user_id)
            )

            if not user_threads:
                logger.critical("no threads found")
                return

            existing_user_context = await context_service.fetch_user_context(
                UUID(user_id)
            )

            existing_context_text = (
                existing_user_context
                if existing_user_context
                else "None - This is the first analysis for the user"
            )

            from . import make_request, USER_CONTEXT_PROMPT

            prompt = USER_CONTEXT_PROMPT.format(
                existing_context=existing_context_text,
                threads_metadata=json.dumps(user_threads, indent=2, default=str),
            )

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes user behaviour patterns and generated context summaries in JSON format.",
                },
                {"role": "user", "content": prompt},
            ]

            result = make_request(
                messages=messages, prompt_cache_key="user_context_analysis"
            )
            response_data = UserContextAIResponse(**result)

            updated_context = response_data.context

            await context_service.get_or_create_context(
                user_id=UUID(user_id), context=updated_context
            )

    asyncio.run(process_active_users())
