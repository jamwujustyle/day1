from sqlalchemy.ext.asyncio import AsyncSession

from ..models.subtitle import Subtitle
from ..repositories.subtitle import SubtitleRepository
from uuid import UUID


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

        subtitle = await self.repo.create_subtitle(
            language=language, text=text, segments=segments, video_id=video_id
        )

        return subtitle

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
