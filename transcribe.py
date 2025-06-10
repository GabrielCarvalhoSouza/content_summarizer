from pathlib import Path
import os

import requests

from youtube import manager

from dotenv import load_dotenv

load_dotenv()

api_url = os.getenv("API_URL")

class TranscriptionError(Exception):
    pass


def transcribe():
    parent_path = Path(__file__).parent
    cache_dir_path = parent_path / "cache"
    video_dir_path = cache_dir_path / manager.yt.video_id
    audio_file_path = video_dir_path / "audio.mp3"
    transcription_file_path = video_dir_path / "transcription.txt"

    if transcription_file_path.exists():
        return
    
    if api_url is None:
        raise TranscriptionError("API_URL is not set")

    with open(audio_file_path, "rb") as f:
        files = {"audio": f}
        response = requests.post(api_url, files=files)

    if response.status_code != 200:
        raise TranscriptionError("Transcription failed")

    transcription_data = response.json().get("transcription", {})
    transcription_text = transcription_data.get("text", "")

    with open(transcription_file_path, "w", encoding="utf-8") as f:
        f.write(transcription_text)