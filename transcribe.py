import os

import requests
from dotenv import load_dotenv

from path_manager import path_manager

load_dotenv()

api_url = os.getenv("API_URL")


class TranscriptionError(Exception):
    pass


def transcribe():
    if path_manager.transcription_file_path.exists():
        return

    if api_url is None:
        raise TranscriptionError("API_URL is not set")

    try:
        with open(path_manager.audio_file_path, "rb") as f:
            files = {"audio": f}
            response = requests.post(api_url, files=files)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise TranscriptionError(f"Failed to transcribe audio: {e}") from e

    transcription_data = response.json().get("transcription", {})
    transcription_text = transcription_data.get("text", "")

    with open(path_manager.transcription_file_path, "w", encoding="utf-8") as f:
        f.write(transcription_text)
