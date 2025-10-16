from celery import shared_task
import asyncio
import json
import openai

from app.videos.services import SubtitleService, VideoService
from app.videos.services.subtitle import get_subtitle_sync_service
from app.videos.schemas.ai import AITranslation, AIMultiLanguageTranslation

from ..configs.database import SyncSessionLocal, AsyncSessionLocal


@shared_task
def transcribe_to_english(video_id: str, source_language: str):
    from . import OPENAI_KEY, TRANSLATION_PROMPT

    openai.api_key = OPENAI_KEY

    db = SyncSessionLocal()
    try:
        source_subtitle = get_subtitle_sync_service(db, video_id, source_language)
        if not source_subtitle:
            print(
                f"Source subtitle in {source_language} not found for video {video_id}"
            )
            return

        duration = (
            source_subtitle.segments[-1]["end"] if source_subtitle.segments else 0
        )
        english_instructions = "\n5. Generate a compressed context — a concise yet complete version that preserves all key information while removing unnecessary detail."
        json_keys = "\n- 'compressed_context': 'context_text'"

        prompt = TRANSLATION_PROMPT.format(
            source_language=source_language,
            language="english",
            duration=duration,
            source_text=source_subtitle.text,
            segments=json.dumps(source_subtitle.segments),
            json_keys=json_keys,
            english_instructions=english_instructions,
        )

        response = openai.chat.completions.create(
            # FIXME: TOGGLE MODELS
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides translations and adjusts timestamps in JSON format.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            prompt_cache_key="english_translation",
        )

        response_data = AITranslation.model_validate_json(
            response.choices[0].message.content
        )

        async def save_data():
            async_db = AsyncSessionLocal()
            try:
                subtitle_service = SubtitleService(async_db)
                video_service = VideoService(async_db)

                await subtitle_service.create_subtitle_from_transcription(
                    video_id=video_id,
                    language="english",
                    transcription_data=response_data,
                )
                await video_service.create_localization(
                    video_id=video_id,
                    language="english",
                    title=response_data.title,
                    summary=response_data.summary,
                )
                if response_data.compressed_context:
                    from app.videos.models import Video
                    from app.logs.services import LogService
                    from . import process_log_threading

                    video: Video = await async_db.get(Video, video_id)
                    if video:
                        log_service = LogService(async_db)
                        log = await log_service.create_log(
                            compressed_context=response_data.compressed_context,
                            user_id=video.user_id,
                            video_id=video_id,
                        )
                        process_log_threading.delay(
                            log_id=str(log.id),
                            compressed_context=response_data.compressed_context,
                            user_id=str(video.user_id),
                        )
            finally:
                await async_db.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(save_data())

        # Trigger the next task for other languages
        transcribe_other_languages_batch.delay(
            video_id=video_id, source_language=source_language
        )

    except Exception as ex:
        db.rollback()
        print(f"Error translating to English: {ex}")
        raise ex
    finally:
        db.close()


@shared_task
def transcribe_other_languages_batch(video_id: str, source_language: str):
    from . import OPENAI_KEY, MULTI_LANGUAGE_TRANSLATION_PROMPT, LANGUAGE_MAP

    openai.api_key = OPENAI_KEY

    db = SyncSessionLocal()
    try:
        source_subtitle = get_subtitle_sync_service(db, video_id, source_language)
        if not source_subtitle:
            print(
                f"Source subtitle in {source_language} not found for video {video_id}"
            )
            return

        duration = (
            source_subtitle.segments[-1]["end"] if source_subtitle.segments else 0
        )
        target_languages = [lang for lang in LANGUAGE_MAP.keys() if lang != "english"]

        if not target_languages:
            print("No other languages to translate.")
            return

        prompt = MULTI_LANGUAGE_TRANSLATION_PROMPT.format(
            source_language=source_language,
            target_languages=", ".join(target_languages),
            duration=duration,
            source_text=source_subtitle.text,
            segments=json.dumps(source_subtitle.segments),
        )

        response = openai.chat.completions.create(
            # FIXME: TOGGLE MODELS
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides translations for multiple languages in a single JSON object.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            prompt_cache_key="batch_translation",
        )

        response_data = AIMultiLanguageTranslation.model_validate_json(
            response.choices[0].message.content
        )

        async def save_data():
            async_db = AsyncSessionLocal()
            try:
                subtitle_service = SubtitleService(async_db)
                video_service = VideoService(async_db)
                for lang, data in response_data.translations.items():
                    if lang == source_language:
                        await video_service.update_localization(
                            video_id=video_id,
                            language=lang,
                            title=data.title,
                            summary=data.summary,
                        )
                    else:
                        await subtitle_service.create_subtitle_from_transcription(
                            video_id=video_id,
                            language=lang,
                            transcription_data=data,
                        )
                        await video_service.create_localization(
                            video_id=video_id,
                            language=lang,
                            title=data.title,
                            summary=data.summary,
                        )
            finally:
                await async_db.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(save_data())

    except Exception as ex:
        db.rollback()
        print(f"Error translating to other languages: {ex}")
        raise ex
    finally:
        db.close()


@shared_task
def generate_subtitles_for_video(video_id: str, source_language: str = None):
    from . import LANGUAGE_MAP

    if "english" in LANGUAGE_MAP and source_language != "english":
        transcribe_to_english.delay(video_id=video_id, source_language=source_language)
    else:
        # If the source is English, just translate the others
        transcribe_other_languages_batch.delay(
            video_id=video_id, source_language=source_language
        )
