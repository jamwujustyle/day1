# app/tasks/threading.py
from celery import shared_task
from uuid import UUID
import asyncio
import json
import openai

from app.configs.database import AsyncSessionLocal
from app.logs.services import LogService, ThreadService
from app.logs.schemas import OpenAIThreadResponse


@shared_task
def process_log_threading(
    log_id: str,
    compressed_context: str,
    user_id: str,
):

    async def analyze_and_thread():
        async_db = AsyncSessionLocal()
        try:
            thread_service = ThreadService(async_db)
            log_service = LogService(async_db)

            # Fetch thread metadata
            thread_metadata = await thread_service.fetch_all_user_thread_metadata(
                user_id=UUID(user_id)
            )

            # Build prompt
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
                prompt = f"""You are an intelligent content analyzer.

**Existing Threads:**
{threads_text}

**New Video Compressed Context:**
{compressed_context}

**Your task:**
1.  Analyze the new video context and compare it with the existing threads.
2.  **If it matches an existing thread**:
    a.  Indicate which thread it matches (use the 1-based index).
    b.  Decide if the new context adds significant information to the matched thread.
    c.  If it does, provide an **updated** summary and keywords for that thread. The new summary should integrate the new information, not just append it.
3.  **If it does NOT match any existing thread**:
    a.  Decide if the content is substantial enough to create a **new** thread.
    b.  If yes, generate the thread metadata (name, summary, keywords) for the new thread.

**Response Format (JSON):**
{{
    "match_found": true/false,
    "matched_thread_index": <number 1-based> (null if no match),
    "update_required": true/false (only relevant if a match is found),
    "updated_metadata": {{
        "summary": "Updated summary text",
        "keywords": ["new", "keyword", "list"]
    }} (null if no update is required),
    "should_create_new_thread": true/false (only relevant if no match is found),
    "new_thread_metadata": {{
        "name": "New thread name (max 60 chars)",
        "summary": "Brief summary (max 200 chars)",
        "keywords": ["keyword1", "keyword2"]
    }} (null if a new thread should not be created),
    "reasoning": "Brief explanation of your decision process."
}}

**Guidelines for "update_required":**
- true: The new log adds valuable details, context, or corrects/expands on the existing summary.
- false: The new log is redundant, trivial, or doesn't add significant value to the thread's summary.

**Guidelines for "should_create_new_thread":**
- true: Content is informative, reusable knowledge, part of a larger topic.
- false: Casual/trivial content, test videos, low-value content.
"""
            else:
                # No existing threads
                prompt = f"""You are an intelligent content analyzer.

**Video Compressed Context:**
{compressed_context}

**Your task:**
Since there are no existing threads, decide if this video content is substantial/meaningful enough to warrant creating the FIRST thread. If yes, generate the thread metadata.

**Response Format (JSON):**
{{
    "match_found": false,
    "matched_thread_index": null,
    "update_required": false,
    "updated_metadata": null,
    "should_create_new_thread": true/false,
    "new_thread_metadata": {{
        "name": "New thread name (max 60 chars)",
        "summary": "Brief summary (max 200 chars)",
        "keywords": ["keyword1", "keyword2"]
    }} (null if a new thread should not be created),
    "reasoning": "Brief explanation of your decision process."
}}

**Guidelines for "should_create_new_thread":**
- true: Content is informative, reusable knowledge, part of a larger topic.
- false: Casual/trivial content, test videos, low-value content.
"""

            response = openai.chat.completions.create(
                # FIXME: TOGGLE MODELS
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at content organization. Be thoughtful - quality over quantity.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            print(
                f"AI Threading Decision for log {log_id}: {json.dumps(result, indent=2)}"
            )

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
                    print(
                        f"✓ Linked log {log_id} to existing thread '{target_thread_meta['name']}'"
                    )

                    # Check if an update is required
                    if response_data.update_required and response_data.updated_metadata:
                        updated_meta = response_data.updated_metadata
                        updated_thread = await thread_service.update_thread_metadata(
                            thread_id=target_thread_id,
                            summary=updated_meta.summary,
                            keywords=updated_meta.keywords,
                        )
                        if updated_thread:
                            print(f"  ✓ Updated thread summary and keywords.")
                            print(f"    New Summary: {updated_thread.summary}")
                            print(f"    New Keywords: {updated_thread.keywords}")
                        else:
                            print(f"  ✗ Failed to update thread {target_thread_id}.")
                    else:
                        print("  - No update required for the thread.")
                    print(f"  Reasoning: {reasoning}")

                else:
                    print(f"✗ Invalid thread index received: {thread_index}")

            elif response_data.should_create_new_thread:
                print(f"✓ Log {log_id} is worth threading (no existing match).")
                print(f"  Reasoning: {reasoning}")

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
                    print(f"✓ Created new thread '{thread.name}' (ID: {thread.id})")
                    print(f"  Summary: {thread.summary}")
                    print(f"  Keywords: {thread.keywords}")
                    print(f"✓ Linked log {log_id} to the new thread.")
                else:
                    print("✗ AI suggested creating a thread but provided no metadata.")

            else:
                print(f"✗ Log {log_id} is not worth threading.")
                print(f"  Reasoning: {reasoning}")
        except Exception as ex:
            print(f"Error processing thread for log {log_id}: {ex}")
            raise ex
        finally:
            await async_db.close()

    asyncio.run(analyze_and_thread())
