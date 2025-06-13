import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

api_url = os.getenv("API_URL")


class TranscriptionError(Exception):
    pass


def fetch_transcription(
    api_url: str, transcription_file_path: Path, audio_file_path: Path
):
    if transcription_file_path.exists():
        return

    try:
        with open(audio_file_path, "rb") as f:
            files = {"audio": f}
            response = requests.post(api_url, files=files)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise TranscriptionError(f"Failed to transcribe audio: {e}") from e

    transcription_data = response.json().get("transcription", {})
    transcription_text = transcription_data.get("text", "")

    with open(transcription_file_path, "w", encoding="utf-8") as f:
        f.write(transcription_text)
