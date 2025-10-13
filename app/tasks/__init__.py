from .trimming import trim_silence
from .transcribing import generate_subtitles_for_video, transcribe_to_language
from decouple import config

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
LAB_KEY = config("ELEVENLABS_API_KEY", default="")
OPENAI_KEY = config("OPENAI_API_KEY", default="")
