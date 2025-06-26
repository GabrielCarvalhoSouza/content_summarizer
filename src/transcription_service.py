import json
import logging
from pathlib import Path
from typing import IO

import requests

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    pass


def fetch_transcription(
    api_url: str, transcription_file_path: Path, audio_file_path: Path, api_key: str
) -> None:
    if transcription_file_path.exists():
        logger.info("Transcription file already exists, skipping transcription")
        return

    try:
        with audio_file_path.open("rb") as f:
            files: dict[str, IO[bytes]] = {"audio": f}
            response: requests.Response = requests.post(
                api_url, files=files, timeout=600, headers={"X-Api-Key": api_key}
            )
        response.raise_for_status()
        transcription_text: str = response.json().get("transcription", "")

        with transcription_file_path.open("w", encoding="utf-8") as f:
            f.write(transcription_text)

        logger.info("Transcribed audio successfully")
    except requests.exceptions.RequestException as e:
        logger.error("Failed to transcribe audio", exc_info=True)
        raise TranscriptionError(f"Failed to transcribe audio: {e}") from e
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON response", exc_info=True)
        raise TranscriptionError(f"Failed to parse JSON response: {e}") from e
