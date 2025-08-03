"""Handles audio processing operations using FFmpeg.

This module provides a class that wraps FFmpeg command-line operations,
such as audio acceleration, abstracting the subprocess management
and error handling away from the main application logic.

"""

import logging
import shutil
import subprocess
from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


class AudioProcessingError(Exception):
    """Custom exception for errors during audio processing."""


class AudioProcessor:
    """A class to process audio files using FFmpeg.

    This class requires FFmpeg to be installed and available in the system's
    PATH.

    Attributes:
        _input_path: The path to the source audio file.
        _output_path: The path where the processed audio will be saved.

    """

    def __init__(self, input_path: Path, output_path: Path) -> None:
        """Initialize the AudioProcessor.

        Args:
            input_path: The input audio file path.
            output_path: The output audio file path.

        """
        self._input_path = input_path
        self._output_path = output_path

    def accelerate_audio(self, speed_factor: float) -> None:
        """Accelerates the audio file by a given factor.

        This method relies on the FFmpeg command-line tool. It will overwrite
        the output file if it already exists.

        Args:
            speed_factor: The factor by which to accelerate the audio (e.g., 1.5).

        Raises:
            AudioProcessingError: If the input file is not found, if FFmpeg
                            is not installed, or if the FFmpeg command fails.

        """
        if not self._input_path.exists():
            logger.error("Input audio file does not exist")
            raise AudioProcessingError("Input audio file does not exist")
        if speed_factor == 1.0:
            shutil.copy(self._input_path, self._output_path)
            logger.warning("Speed factor is 1.0, skipping audio acceleration")
            return
        _speed_factor = str(speed_factor)
        ffmpeg = [
            "ffmpeg",
            "-y",
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
            raise AudioProcessingError("Audio acceleration found an error") from e
        except FileNotFoundError as e:
            msg = "FFmpeg not found. Ensure it is installed and in the system's PATH."
            logger.exception(msg)
            raise AudioProcessingError(msg) from e
