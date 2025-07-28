"""Provides a function to interact with the transcription API service."""

import json
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import IO

import requests
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment

logger: logging.Logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """An exception raised when there is an error during transcription."""

    pass


def fetch_transcription_local(
    audio_file_path: Path, whisper_model_name: str, beam_size: int, device: str
) -> str:
    compute_type: str = "auto"
    if device == "cpu":
        compute_type = "int8"
    try:
        whisper_model = WhisperModel(
            whisper_model_name, device=device, compute_type=compute_type
        )
        logger.info("Initializing transcription")

        segments: Iterable[Segment]
        segments, _ = whisper_model.transcribe(
            str(audio_file_path), beam_size=beam_size
        )
        transcription_text: str = "".join(segment.text for segment in segments)

        logger.info("Transcription completed")
        return transcription_text

    except Exception as e:
        logger.error("Error during transcription: %s", e)
        raise TranscriptionError(f"Error during transcription: {e}") from e


def fetch_transcription_api(api_url: str, audio_file_path: Path, api_key: str) -> str:
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
