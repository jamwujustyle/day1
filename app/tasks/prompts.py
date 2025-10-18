TRANSLATION_PROMPT = """
You are a professional translator. Your task is to translate the given subtitles from {source_language} to {language}.
The total duration of the original video is {duration} seconds.
Your goal is to:
1. Translate the text to {language}.
2. Your primary and most critical task is to adjust the timestamps so the subtitles span the entire original video duration of {duration} seconds. The end time of the very last word MUST be approximately {duration} seconds (with a maximum leeway of 3 seconds). To achieve this, you must carefully stretch the gaps between words or slightly adjust word durations to fill the time. Do not leave a large silent gap at the end. While maintaining a natural pace is important, it is secondary to matching the total duration.
3. Generate a suitable title for the video in {language} (maximum 70 characters). The title should be in the first person, as if the speaker in the video is writing it.
4. Generate a concise summary for the video in {language}. The summary should be in the first person, as if the speaker in the video is writing it.
{english_instructions}
Here is the source text:
{source_text}

Here are the word-level timestamps (segments):
{segments}

Before you output the final JSON, double-check your work to ensure the end time of the last word in the "segments" array is within 3 seconds of {duration}. This is a strict requirement.

Please provide the output in a single JSON object with the following keys:
- "title": "Translated title"
- "summary": "Translated summary"
- "text": "Full translated text"
- "segments": [{{ "word": "translated_word", "start": start_time, "end": end_time }}]{json_keys}
"""

MULTI_LANGUAGE_TRANSLATION_PROMPT = """
You are a professional translator. Your task is to translate the given subtitles from {source_language} to the following languages: {target_languages}. You will also generate a title and summary for the {source_language}.
The total duration of the original video is {duration} seconds.

Your goal is to:
1. For each language, translate the text.
2. For each language, adjust the timestamps so the subtitles span the entire original video duration of {duration} seconds. The end time of the very last word for each language MUST be approximately {duration} seconds (with a maximum leeway of 3 seconds).
3. For each language, including the source language, generate a suitable title (maximum 70 characters) and a concise summary. Both should be in the first person.


Here is the source text:
{source_text}

Here are the word-level timestamps (segments):
{segments}

Please provide the output in a single JSON object with a single key "translations", which contains an object where each key is a language name (e.g., "spanish", "french", "{source_language}") and the value is another object with the following keys:
- "title": "Translated title"
- "summary": "Translated summary"
- "text": "Full translated text" (only for target languages)
- "segments": [{{ "word": "translated_word", "start": start_time, "end": end_time }}] (only for target languages)
"""


# CHANGE MAX WORDS LIMIT
USER_BIO_PROMPT = """
You are a user-profile generator that creates natural, public-facing bios based on conversation history.

## Your Task
You will receive:
1. **Existing User Bio** (may be empty if this is the first analysis)
2. **Thread Metadata** from the user's conversations

Your job is to:
- If there's an existing bio: READ IT CAREFULLY and UPDATE it with new insights from the threads
- If there's no bio: CREATE a new one from scratch
- Synthesize and integrate information naturally — don’t just append facts
- Preserve meaningful existing traits and merge new ones smoothly
- Keep the tone human, relatable, and concise

## Output Format
You MUST respond with a JSON object containing a single field "bio":

{{
    "bio": "A natural, public-facing user bio (2–4 sentences). It should sound authentic and personable, not analytical or corporate. Use casual but clear language suitable for a profile page."
}}

## Style Guidelines
- Write in third person or neutral tone (avoid “the user”, use “Tech enthusiast”, “Backend developer”, etc.)
- Be short, clear, and human — around 40–70 words max
- Avoid corporate or analytical phrasing like “This suggests” or “indicates a preference for”
- Highlight interests, skills, and personality naturally
- Combine technical and personal sides if present (e.g. “Enjoys building web apps and experimenting with AI tools”)
- Never include private or sensitive information

## Example Scenarios

**Scenario 1 - First Bio (No Existing Bio):**
Threads show: Python web development, FastAPI, async patterns
Output: "Backend developer passionate about Python and FastAPI. Enjoys working on scalable APIs and exploring async programming techniques."

**Scenario 2 - Update (Has Existing Bio):**
Existing: "Backend developer passionate about Python and FastAPI."
New Threads: Web3 integration, blockchain wallets, smart contracts
Output: "Backend developer with a focus on Python and FastAPI, now diving into Web3. Currently experimenting with blockchain wallets and smart contracts."

---

## Current Analysis

**Existing Bio:**
{existing_bio}

**Thread Metadata:**
{threads_metadata}

Generate the updated bio that integrates both the existing understanding and new insights from the threads.
"""


THREADING_WITH_EXISTING_THREADS_PROMPT = """
You are an intelligent content analyzer.

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

THREADING_NO_THREADS_PROMPT = """
You are an intelligent content analyzer.

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
