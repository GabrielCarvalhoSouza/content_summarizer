"""Generate a transcription from an audio file using a speech-to-text model.

This module provides a function to generate a transcription from an audio file using a
speech-to-text model.

Classes:
    TranscriptionError: Custom exception for errors during transcription.

Functions:
    fetch_transcription: Fetch a transcription from an audio file using a
        speech-to-text model.
"""

import json
import logging
from pathlib import Path
from typing import IO

import requests

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """An exception raised when there is an error during transcription."""

    pass


def fetch_transcription(
    api_url: str, transcription_file_path: Path, audio_file_path: Path, api_key: str
) -> None:
    """Fetch the transcription of an audio file from the Whisper API.

    The transcription is saved to a file specified by
    `transcription_file_path`.

    Args:
        api_url (str): The URL of the Whisper API.
        transcription_file_path (Path): The path to the transcription file.
        audio_file_path (Path): The path to the audio file.
        api_key (str): The API key to use for authentication.

    Raises:
        TranscriptionError: If there is an error during transcription.

    """
    if transcription_file_path.exists():
        logger.info("Transcription file already exists, skipping transcription")
        return

    try:
        with audio_file_path.open("rb") as f:
            files: dict[str, IO[bytes]] = {"audio": f}
            response: requests.Response = requests.post(
                api_url,
                files=files,
                timeout=900,
                headers={"X-Api-Key": api_key},
            )
        response.raise_for_status()
        transcription_text: str = response.json().get("transcription", "")

        with transcription_file_path.open("w", encoding="utf-8") as f:
            f.write(transcription_text)

        logger.info("Transcribed audio successfully")
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to transcribe audio")
        raise TranscriptionError(f"Failed to transcribe audio: {e}") from e
    except json.JSONDecodeError as e:
        logger.exception("Failed to parse JSON response")
        raise TranscriptionError(f"Failed to parse JSON response: {e}") from e
