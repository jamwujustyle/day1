from moviepy import VideoFileClip

import openai
import os

openai.api_key = ""

video_path = "ref/20250929_205130.mp4"

clip = VideoFileClip(video_path)
clip.audio.write_audiofile("/tmp/test_audio.wav")
clip.close()

with open("/tmp/test_audio.wav", "rb") as audio_file:
    transcription = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="hi",
        response_format="verbose_json",
        timestamp_granularities=["word"],
    )


print(transcription)
