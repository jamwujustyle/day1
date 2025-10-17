from .trimming import trim_silence
from .threading import process_log_threading
from .speech_to_text import transcribe_source_audio
from .transcribing import (
    generate_subtitles_for_video,
    transcribe_to_english,
    transcribe_other_languages_batch,
)
import openai
from .prompts import TRANSLATION_PROMPT, MULTI_LANGUAGE_TRANSLATION_PROMPT

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
