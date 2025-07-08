"""Handles audio processing tasks, such as acceleration, using FFmpeg."""

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioProcessingError(Exception):
    """An exception raised when there is an error during audio processing."""


class AudioProcessor:
    """A class to process audio files.

    Args:
        input_path (Path): The path to the source audio file.
        output_path (Path): The path where the processed audio file will be saved.

    """

    def __init__(self, input_path: Path, output_path: Path) -> None:
        """Initialize the AudioProcessor.

        Args:
            input_path (Path): The input audio file path.
            output_path (Path): The output audio file path.

        """
        self._input_path = input_path
        self._output_path = output_path

    def accelerate_audio(self, speed_factor: float) -> None:
        """Accelerates the audio file by a given factor using FFmpeg.

        This method overwrites the output file if it already exists.
        It relies on the calling pipeline to manage caching.

        Args:
            speed_factor (float): The factor by which to accelerate the audio.

        Raises:
            AudioProcessingError: If the input file is not found or if the
                                  FFmpeg command fails.

        """
        _speed_factor = str(speed_factor)
        if not self._input_path.exists():
            logger.error("Input audio file does not exist")
            raise AudioProcessingError("Input audio file does not exist")
        if _speed_factor == "1.0":
            shutil.copy(self._input_path, self._output_path)
            logger.warning("Speed factor is 1.0, skipping audio acceleration")
            return
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
            raise AudioProcessingError(f"Audio acceleration found an error: {e}") from e
        except FileNotFoundError as e:
            logger.exception("FFmpeg not found: %s", e)
            raise AudioProcessingError(f"FFmpeg not found: {e}") from e
