from pathlib import Path
from typing import IO, Any

import requests


class TranscriptionError(Exception):
    pass


def fetch_transcription(
    api_url: str, transcription_file_path: Path, audio_file_path: Path
) -> None:
    if transcription_file_path.exists():
        return

    try:
        with open(audio_file_path, "rb") as f:
            files: dict[str, IO[bytes]] = {"audio": f}
            response: requests.Response = requests.post(api_url, files=files)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise TranscriptionError(f"Failed to transcribe audio: {e}") from e

    transcription_data: dict[str, Any] = response.json().get("transcription", {})
    transcription_text: str = transcription_data.get("text", "")

    with open(transcription_file_path, "w", encoding="utf-8") as f:
        f.write(transcription_text)
