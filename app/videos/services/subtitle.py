from sqlalchemy.ext.asyncio import AsyncSession

from ..models.subtitle import Subtitle
from ..repositories.subtitle import SubtitleRepository


class SubtitleService:
    def __init__(self, db: AsyncSession):
        self.repo = SubtitleRepository(db)

    async def create_subtitle_from_transcription(
        self, transcription_data, video_id, language
    ) -> Subtitle:
        if isinstance(transcription_data, dict):
            text = transcription_data.get("text")
            words_data = transcription_data.get("segments", [])
            segments = [
                {
                    "word": w.get("word"),
                    "start": w.get("start"),
                    "end": w.get("end"),
                }
                for w in words_data
            ]
        else:  # Assumes it's the OpenAI response object
            text = transcription_data.text
            words_data = transcription_data.words
            segments = [
                {"word": w.word, "start": w.start, "end": w.end} for w in words_data
            ]

        print(segments)

        # TODO: CHANGE

        subtitle = await self.repo.create_subtitle(
            language=language, text=text, segments=segments, video_id=video_id
        )

        return subtitle
