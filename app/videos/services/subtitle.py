from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..models.subtitle import Subtitle
from ..repositories.subtitle import SubtitleRepository, get_subtitle_sync
from ..schemas.ai import AITranslation
from uuid import UUID


class SubtitleService:
    def __init__(self, db: AsyncSession):
        self.repo = SubtitleRepository(db)

    async def create_subtitle_from_transcription(
        self, transcription_data: AITranslation, video_id: UUID, language: str
    ) -> Subtitle:
        segments = [
            {"word": s.word, "start": s.start, "end": s.end}
            for s in transcription_data.segments
        ]
        subtitle = await self.repo.create_subtitle(
            language=language,
            text=transcription_data.text,
            segments=segments,
            video_id=video_id,
        )
        return subtitle

    async def get_subtitle(self, language, video_id) -> Subtitle:
        return await self.repo.get_subtitle(language, video_id)

    async def get_subtitle_as_vtt(self, subtitle_id: UUID) -> str:
        subtitle = await self.repo.get_subtitle_by_id(subtitle_id)
        if not subtitle or not subtitle.segments:
            return ""

        vtt_content = "WEBVTT\n\n"

        words_per_line = 7
        num_segments = len(subtitle.segments)

        i = 0
        while i < num_segments:
            line_segments = subtitle.segments[i : i + words_per_line]

            start_time = self._format_timestamp(line_segments[0]["start"])
            end_time = self._format_timestamp(line_segments[-1]["end"])
            line_text = " ".join(segment["word"].strip() for segment in line_segments)

            vtt_content += f"{start_time} --> {end_time}\n{line_text}\n\n"

            i += words_per_line

        return vtt_content

    def _format_timestamp(self, seconds: float) -> str:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours):02}:{int(minutes):02}:{seconds:06.3f}"


def get_subtitle_sync_service(
    db: Session, video_id: str, language: str
) -> Subtitle | None:
    return get_subtitle_sync(db, video_id, language)
