from celery import shared_task, group
from sqlalchemy import select
import asyncio
import json
import openai

from app.videos.models import VideoLocalization, Subtitle
from app.videos.services import SubtitleService, VideoService
from app.logs.services import LogService

from ..configs.database import SyncSessionLocal, AsyncSessionLocal


@shared_task
def transcribe_to_language(
    video_id: str, language: str, lang_code: str, source_language: str
):
    from . import OPENAI_KEY, TRANSLATION_PROMPT

    openai.api_key = OPENAI_KEY

    db = SyncSessionLocal()
    try:
        source_subtitle = db.execute(
            select(Subtitle).where(
                (Subtitle.video_id == video_id) & (Subtitle.language == source_language)
            )
        ).scalar_one_or_none()

        if not source_subtitle:
            print(
                f"Source subtitle in {source_language} not found for video {video_id}"
            )
            return

        duration = (
            source_subtitle.segments[-1]["end"] if source_subtitle.segments else 0
        )
        english_instructions = ""
        json_keys = ""

        if language.lower() == "english":
            english_instructions = "\n5. Generate a compressed context — a concise yet complete version that preserves all key information while removing unnecessary detail."
            json_keys = "\n- 'compressed_context': 'context_text'"

        prompt = TRANSLATION_PROMPT.format(
            source_language=source_language,
            language=language,
            duration=duration,
            source_text=source_subtitle.text,
            segments=json.dumps(source_subtitle.segments),
            json_keys=json_keys,
            english_instructions=english_instructions,
        )
        if language.lower() == "english":
            print(f"english prompt:\n{prompt}")

        response = openai.chat.completions.create(
            model="gpt-5",  # Or "gpt-5" when available
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides translations and adjusts timestamps in JSON format.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)

        async def save_data():
            async_db = AsyncSessionLocal()
            try:
                subtitle_service = SubtitleService(async_db)
                video_service = VideoService(async_db)

                # Create new subtitle
                await subtitle_service.create_subtitle_from_transcription(
                    video_id=video_id,
                    language=language,
                    transcription_data={
                        "text": result["text"],
                        "segments": result["segments"],
                    },
                )
                # create localization
                await video_service.create_localization(
                    video_id=video_id,
                    language=language,
                    title=result["title"],
                    summary=result["summary"],
                )
                # runs conditionally
                if language.lower() == "english" and "compressed_context" in result:
                    from app.configs.logging_config import logger

                    logger.critical("entered if english block")
                    from app.videos.models import Video
                    from app.logs.services import LogService
                    from . import process_log_threading

                    video: Video = await async_db.get(Video, video_id)

                    if video:
                        log_service = LogService(async_db)
                        log = await log_service.create_log(
                            compressed_context=result["compressed_context"],
                            user_id=video.user_id,
                            video_id=video_id,
                        )
                        print(
                            f"log created for video with context: {video_id}: {log.id}: {result['compressed_context']}"
                        )

                        process_log_threading.delay(
                            log_id=str(log.id),
                            compressed_context=result["compressed_context"],
                            user_id=str(video.user_id),
                        )
            finally:
                await async_db.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(save_data())

    except Exception as ex:
        db.rollback()
        print(f"Error translating to {language}: {ex}")
        raise ex
    finally:
        db.close()


@shared_task
def generate_subtitles_for_video(video_id: str, source_language: str = None):
    from . import LANGUAGE_MAP

    # Prioritize English transcription for faster threading
    if "english" in LANGUAGE_MAP and source_language != "english":
        print(f"Prioritizing English transcription for video: {video_id}")
        transcribe_to_language.apply_async(
            args=[video_id, "english", LANGUAGE_MAP["english"], source_language]
        )

    # Schedule other languages to run concurrently
    other_languages_tasks = []
    for language, lang_code in LANGUAGE_MAP.items():
        if (source_language and source_language == language) or language == "english":
            continue
        print(f"Scheduling transcription for {language} (video: {video_id})")
        other_languages_tasks.append(
            transcribe_to_language.s(video_id, language, lang_code, source_language)
        )

    if not other_languages_tasks:
        print("No other languages to transcribe.")
        return

    transcribe_tasks = group(other_languages_tasks)
    result = transcribe_tasks.apply_async()

    print(f"Started concurrent translation for other languages for video: {video_id}")

    return result.id
