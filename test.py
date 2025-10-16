import openai
import os

OPENAI_KEY = os.getenv("OPENAI_KEY")
openai.api_key = OPENAI_KEY
threads_text = [
    {
        "id": "4ff51836-72eb-45f0-991b-551a52817fb9",
        "name": "ACME NIC-NIC Connector: OOTB Support & Fallbacks",
        "summary": "Custom NIC-NIC connector is being polished with concrete transaction features: tested sponsored vs wallet-paid flows, added a gas-change UI, and verified gas logic. Still targeting out-of-the-box ACME support with multicalls and robust fallbacks.",
        "keywords": [
            "NIC-NIC connector",
            "ACME",
            "out-of-the-box",
            "multicalls",
            "fallbacks",
            "transaction",
            "sponsored transactions",
            "gas UI",
            "gas logic",
            "wallet-paid",
        ],
    }
]

compressed_context = "Daily log: tested NikNik sponsored transactions; built a gas-change UI; verified gas logic for sponsored vs wallet-paid; began a system to record, transcribe, and translate daily video logs for a people-only social network; I debrief like in Avatar; this confirms the work is ongoing."

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


response = openai.chat.completions.create(
    model="gpt-5", messages=[{"role": "user", "content": prompt}]
)


print(f"\n=== Model: {response.model} ===")
print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")
print(f"Total tokens: {response.usage.total_tokens}")
print(f"\nOutput:\n{response.choices[0].message.content}\n")
