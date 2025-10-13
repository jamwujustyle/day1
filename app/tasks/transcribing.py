from celery import shared_task, group
from sqlalchemy import select
import asyncio
import json
import openai

from app.videos.models.subtitle import Subtitle
from app.videos.models.video import Video, VideoLocalization
from app.videos.services.subtitle import SubtitleService

from ..configs.database import SyncSessionLocal, AsyncSessionLocal


@shared_task
def transcribe_to_language(
    video_id: str, language: str, lang_code: str, source_language: str
):
    from . import OPENAI_KEY

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

        prompt = f"""
        You are a professional translator. Your task is to translate the given subtitles from {source_language} to {language}.
        The total duration of the original video is {duration} seconds.
        Your goal is to:
        1. Translate the text to {language}.
        2. Your primary and most critical task is to adjust the timestamps so the subtitles span the entire original video duration of {duration} seconds. The end time of the very last word MUST be approximately {duration} seconds (with a maximum leeway of 3 seconds). To achieve this, you must carefully stretch the gaps between words or slightly adjust word durations to fill the time. Do not leave a large silent gap at the end. While maintaining a natural pace is important, it is secondary to matching the total duration.
        3. Generate a suitable title for the video in {language} (maximum 70 characters).
        4. Generate a concise summary for the video in {language}.

        Here is the source text:
        {source_subtitle.text}

        Here are the word-level timestamps (segments):
        {json.dumps(source_subtitle.segments)}

        Please provide the output in a single JSON object with the following keys:
        - "title": "Translated title"
        - "summary": "Translated summary"
        - "text": "Full translated text"
        - "segments": [{{ "word": "translated_word", "start": start_time, "end": end_time }}]
        """

        response = openai.chat.completions.create(
            model="gpt-4-turbo",  # Or "gpt-5" when available
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

                # Create new subtitle
                await subtitle_service.create_subtitle_from_transcription(
                    video_id=video_id,
                    language=language,
                    transcription_data={
                        "text": result["text"],
                        "segments": result["segments"],
                    },
                )

                # Create or update video localization
                video_localization = VideoLocalization(
                    video_id=video_id,
                    language=language,
                    title=result["title"],
                    summary=result["summary"],
                )
                async_db.add(video_localization)
                await async_db.commit()
            finally:
                await async_db.close()

        asyncio.run(save_data())

    except Exception as ex:
        db.rollback()
        print(f"Error translating to {language}: {ex}")
        raise ex
    finally:
        db.close()


@shared_task
def generate_subtitles_for_video(video_id: str, source_language: str = None):
    from . import LANGUAGE_MAP

    tasks = []
    for language, lang_code in LANGUAGE_MAP.items():
        if source_language and source_language == language:
            continue
        print(f"language={language}, lang_code={lang_code}")
        tasks.append(
            transcribe_to_language.s(video_id, language, lang_code, source_language)
        )

    if not tasks:
        print("No new languages to transcribe.")
        return

    transcribe_tasks = group(tasks)
    result = transcribe_tasks.apply_async()

    print(f"Started concurrent translation for video: {video_id}")

    return result.id
