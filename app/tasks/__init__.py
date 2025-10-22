from .trimming import trim_silence
from .speech_to_text import transcribe_source_audio
from .transcribing import (
    generate_subtitles_for_video,
    transcribe_to_english,
    transcribe_other_languages_batch,
)
from .threading import process_log_threading
from .user_bio import update_user_bio

import openai, json
from .prompts import (
    TRANSLATION_PROMPT,
    MULTI_LANGUAGE_TRANSLATION_PROMPT,
    USER_BIO_PROMPT,
)

from app.configs.logging_config import logger
from app.configs.settings import get_settings

settings = get_settings()

LANGUAGE_MAP = {
    "english": "en",
    "spanish": "es",
    "mandarin": "zh",
    "french": "fr",
    "hindi": "hi",
    "russian": "ru",
    "arabic": "ar",
    "portuguese": "pt",
}

MEDIA_ROOT = "media/videos"
OPENAI_KEY = settings.OPENAI_API_KEY
openai.api_key = OPENAI_KEY


def make_request(
    messages: list,
    model="gpt-4.1-mini",
    response_format={"type": "json_object"},
    prompt_cache_key: str = None,
    temperature: float = 1,
    **kwargs,
):
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            response_format=response_format,
            prompt_cache_key=prompt_cache_key,
            temperature=temperature,
        )
        content = response.choices[0].message.content
        logger.debug(f"AI response: {content}")

        if response_format.get("type") == "json_object":
            return json.loads(content)
        return content
    except Exception as ex:
        logger.critical(f"[OpenAI Error] {str(ex)}")
        raise
