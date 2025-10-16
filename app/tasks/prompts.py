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
