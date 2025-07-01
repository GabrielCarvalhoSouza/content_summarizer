"""Audio processor module.

This module provides a class to process audio files using FFmpeg.

Classes:
    AudioProcessor: A class to process audio files using FFmpeg.
    AudioProcessingError: An exception raised when there is an error during audio
        processing.

"""

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioProcessingError(Exception):
    """An exception raised when there is an error during audio processing."""


class AudioProcessor:
    """A class to process audio files using FFmpeg."""

    def __init__(self, input_path: Path, output_path: Path) -> None:
        """Initialize the AudioProcessor.

        Args:
            input_path (Path): The input audio file path.
            output_path (Path): The output audio file path.

        """
        self._input_path = input_path
        self._output_path = output_path

    def accelerate_audio(self, speed_factor: float) -> None:
        """Accelerate audio by a given speed factor using FFmpeg.

        Args:
            speed_factor (float): The speed factor to accelerate the audio by.

        Raises:
            AudioProcessingError: If there is an error during audio processing.
            FileNotFoundError: If FFmpeg is not found.

        """
        _speed_factor = str(speed_factor)
        if self._output_path.exists():
            logger.info("Output audio file already exists, skipping audio acceleration")
            return
        if not self._input_path.exists():
            logger.error("Input audio file does not exist")
            raise AudioProcessingError("Input audio file does not exist")
        if _speed_factor == "1.0":
            shutil.copy(self._input_path, self._output_path)
            logger.info("Speed factor is 1.0, skipping audio acceleration")
            return
        ffmpeg = [
            "ffmpeg",
            "-i",
            str(self._input_path),
            "-filter:a",
            f"atempo={_speed_factor}",
            str(self._output_path),
        ]
        try:
            subprocess.run(ffmpeg, check=True, capture_output=True, text=True)
            logger.info(f"Audio accelerated {_speed_factor}x successfully")
        except subprocess.CalledProcessError as e:
            logger.exception("Audio acceleration found an error: %s", e.stderr)
            raise AudioProcessingError(f"Audio acceleration found an error: {e}") from e
        except FileNotFoundError as e:
            logger.exception("FFmpeg not found: %s", e)
            raise AudioProcessingError(f"FFmpeg not found: {e}") from e
