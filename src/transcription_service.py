"""Provides a function to interact with the transcription API service."""

import json
import logging
from pathlib import Path
from typing import IO

import requests

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """An exception raised when there is an error during transcription."""

    pass


def fetch_transcription(api_url: str, audio_file_path: Path, api_key: str) -> str:
    """Send an audio file to the transcription API and returns the transcribed text.

    This function handles the API request and error handling, returning the
    transcription text in memory. It does not handle caching or file saving.

    Args:
        api_url (str): The URL of the transcription API endpoint.
        audio_file_path (Path): The path to the audio file to be transcribed.
        api_key (str): The API key for authentication.

    Returns:
        str: The transcribed text returned by the API.

    Raises:
        TranscriptionError: If the API request fails or returns an error.

    """
    try:
        with audio_file_path.open("rb") as f:
            files: dict[str, IO[bytes]] = {"audio": f}
            response: requests.Response = requests.post(
                api_url,
                files=files,
                timeout=1800,
                headers={"X-Api-Key": api_key},
            )
        response.raise_for_status()
        transcription_text: str = response.json().get("transcription", "")
        logger.info("Transcribed audio successfully")
        return transcription_text

    except requests.exceptions.RequestException as e:
        logger.exception("Failed to transcribe audio")
        raise TranscriptionError(f"Failed to transcribe audio: {e}") from e
    except json.JSONDecodeError as e:
        logger.exception("Failed to parse JSON response")
        raise TranscriptionError(f"Failed to parse JSON response: {e}") from e
