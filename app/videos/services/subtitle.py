from sqlalchemy.ext.asyncio import AsyncSession

from ..models.subtitle import Subtitle
from ..repositories.subtitle import SubtitleRepository


class SubtitleService:
    def __init__(self, db: AsyncSession):
        self.repo = SubtitleRepository(db)

    async def create_subtitle_from_transcription(
        self, transcription_data, video_id, language
    ) -> Subtitle:
        text = transcription_data.text
        segments = [
            {
                "word": w.word,
                "start": w.start,
                "end": w.end,
            }
            for w in transcription_data.words
        ]

        print(segments)

        # TODO: CHANGE

        subtitle = await self.repo.create_subtitle(
            language=language, text=text, segments=segments, video_id=video_id
        )

        return subtitle
