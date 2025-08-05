"""Manages all dynamic file and directory paths for the application.

This module provides a centralized PathManager class that is responsible
for generating all context-dependent paths, such as for specific videos,
cache files, and configuration. It ensures path consistency and makes
the file structure easier to manage and modify.

"""
# Copyright 2025 Gabriel Carvalho
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Self

from platformdirs import user_cache_path, user_config_path, user_data_path

if TYPE_CHECKING:
    from hashlib import _Hash

app_name = "content-summarizer"
app_author = "Content Summarizer"

logger = logging.getLogger(__name__)


class PathManager:
    """Manages dynamic application paths.

    This class holds the state for a specific execution (like a video ID)
    and generates all necessary file paths based on that state.

    Attributes:
        _video_id: The unique identifier for the content being processed.

    """

    def __init__(self) -> None:
        """Initialize the PathManager."""
        self._video_id: str | None = None

    @staticmethod
    def _get_params_hash(params: dict[str, str]) -> str:
        string_parts: list[str] = []

        for key, value in params.items():
            string_parts.append(f"{key}-{value}")

        str_params: str = "-".join(sorted(string_parts))
        bytes_params: bytes = str_params.encode("utf-8")
        hash_params: _Hash = hashlib.md5(bytes_params)

        return hash_params.hexdigest()[:7]

    @staticmethod
    def sanitize_video_title(video_title: str) -> str:
        """Sanitize a string to be used as a safe filename.

        This method performs the following operations:
        - Converts the string to lowercase.
        - Replaces spaces with hyphens.
        - Collapses multiple consecutive hyphens into a single one.
        - Removes any leading or trailing hyphens.

        Args:
            video_title: The raw string title to be sanitized.

        Returns:
            A sanitized string suitable for use in a filename.

        """
        video_title = video_title.lower()
        video_title = video_title.replace(" ", "-")
        video_title = re.sub(r"-+", "-", video_title)
        return video_title.strip("-")

    def set_video_id(self, video_id: str) -> Self:
        """Set the video ID for the current context.

        This method allows the PathManager to generate video-specific paths.

        Args:
            video_id: The unique identifier for the video.

        Returns:
            The instance of the PathManager.

        """
        self._video_id = video_id
        return self

    def get_accelerated_audio_path(self, speed_factor: float) -> Path:
        """Get the path for the accelerated audio file.

        Args:
            speed_factor: The playback speed multiplier.

        Returns:
            The full path for the speed-adjusted audio file.

        """
        _speed_factor = str(speed_factor)
        return self.video_dir_path / f"audio-{_speed_factor}x.mp3"

    def get_transcription_path(
        self, whisper_model_name: str, speed_factor: float, beam_size: int
    ) -> Path:
        """Get the path for the transcription file based on its parameters.

        Args:
            whisper_model_name: The name of the Whisper model used.
            speed_factor: The audio speed factor used.
            beam_size: The beam size used for transcription.

        Returns:
            The full path for the generated transcription file.

        """
        params: dict[str, str] = {
            "whisper_model_name": whisper_model_name,
            "speed_factor": str(speed_factor),
            "beam_size": str(beam_size),
        }
        return (
            self.video_dir_path / f"transcription-{self._get_params_hash(params)}.txt"
        )

    def get_summary_path(
        self,
        gemini_model_name: str,
        user_language: str,
        whisper_model_name: str,
        speed_factor: float,
        beam_size: int,
    ) -> Path:
        """Get the path for the summary file based on its parameters.

        Args:
            gemini_model_name: The name of the Gemini model used.
            user_language: The target language of the summary.
            whisper_model_name: The name of the Whisper model used for the source.
            speed_factor: The audio speed factor used for the source.
            beam_size: The beam size used for the source transcription.

        Returns:
            The full path for the generated summary file.

        """
        params: dict[str, str] = {
            "gemini_model_name": gemini_model_name,
            "user_language": user_language,
            "whisper_model_name": whisper_model_name,
            "speed_factor": str(speed_factor),
            "beam_size": str(beam_size),
        }
        return self.video_dir_path / f"summary-{self._get_params_hash(params)}.md"

    def get_final_summary_path(self, video_title: str, output_dir: Path) -> Path:
        """Get the path for the final, user-facing summary file.

        This method generates a sanitized, human-readable filename based on the
        video's title and combines it with the user-specified output directory.

        Args:
            video_title: The title of the video to be used for the filename.
            output_dir: The target directory where the file will be saved.

        Returns:
            The full, final path for the summary file.

        """
        safe_title: str = self.sanitize_video_title(video_title)
        return output_dir / f"{safe_title}.md"

    @property
    def video_id(self) -> str:
        """Get the currently configured video ID.

        Raises:
            ValueError: If the video ID has not been set via set_video_id().

        Returns:
            The video ID string.

        """
        if self._video_id is None:
            logger.error("Internal Error: Video ID is not set")
            raise ValueError("Video ID is not set, call set_video_id() first")
        return self._video_id

    @property
    def parent_path(self) -> Path:
        """Get the path of the parent directory of this file.

        Returns:
            Path: The path of the parent directory of this file.

        """
        return Path(__file__).parent

    @property
    def root_path(self) -> Path:
        """Get the root path of the project.

        Returns:
            Path: The root path of the project.

        """
        return self.parent_path.parent

    @property
    def video_dir_path(self) -> Path:
        """Get the path of the directory for the video.

        Returns:
            Path: The path of the directory for the video.

        """
        return self.cache_dir_path / self.video_id

    @property
    def audio_file_path(self) -> Path:
        """Get the path of the audio file.

        Returns:
            Path: The path of the audio file.

        """
        return self.video_dir_path / "audio.mp3"

    @property
    def caption_file_path(self) -> Path:
        """Get the path of the caption file.

        Returns:
            Path: The path of the caption file.

        """
        return self.video_dir_path / "caption.txt"

    @property
    def metadata_file_path(self) -> Path:
        """Get the path of the metadata file.

        Returns:
            Path: The path of the metadata file.

        """
        return self.video_dir_path / "metadata.json"

    @property
    def log_file_path(self) -> Path:
        """Get the path of the log file.

        Returns:
            Path: The path of the log file.

        """
        return user_data_path(app_name, app_author) / "log.log"

    @property
    def config_file_path(self) -> Path:
        """Get the path of the config directory.

        Returns:
            Path: The path of the config directory.

        """
        return user_config_path(app_name, app_author) / "config.json"

    @property
    def cache_dir_path(self) -> Path:
        """Get the path of the cache directory.

        Returns:
            Path: The path of the cache directory.

        """
        return user_cache_path(app_name, app_author)
