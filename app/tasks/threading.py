# app/tasks/threading.py
from celery import shared_task
from uuid import UUID
import asyncio

from app.configs.database import AsyncSessionLocal
from app.logs.services import LogService, ThreadService
from app.logs.schemas import OpenAIThreadResponse
from .lock import get_user_lock
from app.configs.logging_config import logger
from app.configs.logging_config import logger


@shared_task
def process_log_threading(
    log_id: str,
    compressed_context: str,
    user_id: str,
):
    lock = get_user_lock(user_id)

    try:
        acquired = lock.acquire(blocking=True)

        if not acquired:
            logger.critical(f"Failed to acquire lock for user {user_id}")
            raise Exception(f"Could not acquire lock for user {user_id}")

        logger.info(f"🔒 Acquired lock for user {user_id} - processing log {log_id}")

        async def analyze_and_thread():
            async with AsyncSessionLocal() as async_db:
                thread_service = ThreadService(async_db)
                log_service = LogService(async_db)

                # Fetch thread metadata
                thread_metadata = await thread_service.fetch_all_user_thread_metadata(
                    user_id=UUID(user_id)
                )

                # Build prompt
                from .prompts import (
                    THREADING_WITH_EXISTING_THREADS_PROMPT,
                    THREADING_NO_THREADS_PROMPT,
                )

                if thread_metadata:
                    threads_text = "\n".join(
                        [
                            f"Thread {i+1}:\n"
                            f"  Name: {meta['name']}\n"
                            f"  Summary: {meta['summary']}\n"
                            f"  Keywords: {', '.join(meta['keywords'] or [])}\n"
                            for i, meta in enumerate(thread_metadata)
                        ]
                    )
                    prompt = THREADING_WITH_EXISTING_THREADS_PROMPT.format(
                        threads_text=threads_text,
                        compressed_context=compressed_context,
                    )
                else:
                    # No existing threads
                    prompt = THREADING_NO_THREADS_PROMPT.format(
                        compressed_context=compressed_context
                    )

                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert at content organization. Be thoughtful - quality over quantity.",
                    },
                    {"role": "user", "content": prompt},
                ]

                from . import make_request

                result = make_request(messages=messages)

                # Process based on AI decision
                response_data = OpenAIThreadResponse(**result)
                reasoning = response_data.reasoning

                if response_data.match_found:
                    thread_index = response_data.matched_thread_index
                    if thread_index and 1 <= thread_index <= len(thread_metadata):
                        target_thread_meta = thread_metadata[thread_index - 1]
                        target_thread_id = target_thread_meta["id"]

                        # Link log to the matched thread first
                        await log_service.link_log_to_thread(
                            log_id=UUID(log_id), thread_id=target_thread_id
                        )
                        logger.info(
                            f"✓ Linked log {log_id} to existing thread '{target_thread_meta['name']}'"
                        )

                        # Check if an update is required
                        if (
                            response_data.update_required
                            and response_data.updated_metadata
                        ):
                            updated_meta = response_data.updated_metadata
                            updated_thread = (
                                await thread_service.update_thread_metadata(
                                    thread_id=target_thread_id,
                                    summary=updated_meta.summary,
                                    keywords=updated_meta.keywords,
                                )
                            )
                            if updated_thread:
                                logger.info(f"  ✓ Updated thread summary and keywords.")
                                logger.info(
                                    f"    New Summary: {updated_thread.summary}"
                                )
                                logger.info(
                                    f"    New Keywords: {updated_thread.keywords}"
                                )
                            else:
                                logger.error(
                                    f"  ✗ Failed to update thread {target_thread_id}."
                                )
                        else:
                            logger.info("  - No update required for the thread.")
                        logger.info(f"  Reasoning: {reasoning}")

                    else:
                        logger.error(f"✗ Invalid thread index received: {thread_index}")

                elif response_data.should_create_new_thread:
                    logger.info(
                        f"✓ Log {log_id} is worth threading (no existing match)."
                    )
                    logger.info(f"  Reasoning: {reasoning}")

                    if response_data.new_thread_metadata:
                        new_meta = response_data.new_thread_metadata
                        thread = await thread_service.create_thread(
                            name=new_meta.name,
                            summary=new_meta.summary,
                            user_id=UUID(user_id),
                            keywords=new_meta.keywords,
                        )
                        await log_service.link_log_to_thread(
                            log_id=UUID(log_id), thread_id=thread.id
                        )
                        logger.info(
                            f"✓ Created new thread '{thread.name}' (ID: {thread.id})"
                        )
                        logger.info(f"  Summary: {thread.summary}")
                        logger.info(f"  Keywords: {thread.keywords}")
                        logger.info(f"✓ Linked log {log_id} to the new thread.")
                    else:
                        logger.error(
                            "✗ AI suggested creating a thread but provided no metadata."
                        )

                else:
                    logger.info(f"✗ Log {log_id} is not worth threading.")
                    logger.info(f"  Reasoning: {reasoning}")

        # RUN THE ASYNC FUNCTION - ONLY ONE asyncio.run() CALL
        asyncio.run(analyze_and_thread())

    finally:
        # Release lock after async function completes
        try:
            lock.release()
            logger.info(f"🔓 Released lock for user {user_id}")
        except Exception as ex:
            logger.warning(f"Failed to release lock for user {user_id}: {ex}")

    # Trigger user context update
    from .user_bio import update_user_bio

    update_user_bio.delay(user_id=user_id)
