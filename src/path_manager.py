"""Path manager for the content summarizer.

This module provides a custom path manager for the content summarizer.

Classes:
    PathManager: A class to manage paths for the content summarizer.

"""

import logging
from pathlib import Path
from typing import Self

logger = logging.getLogger(__name__)


class PathManager:
    """A class to manage paths for the content summarizer.

    Attributes:
        _parent_path (Path): The path of the parent directory of this file.
        _root_path (Path): The root path of the project.
        _video_id (str | None): The video ID to be processed.

    """

    def __init__(self) -> None:
        """Initialize the PathManager."""
        self._parent_path: Path = Path(__file__).parent
        self._root_path: Path = self._parent_path.parent
        self._video_id: str | None = None

    def set_video_id(self, video_id: str) -> Self:
        """Set the video ID to be processed.

        Args:
            video_id (str): The video ID.

        Returns:
            Self: The PathManager instance.

        """
        self._video_id = video_id
        return self

    @property
    def video_id(self) -> str:
        """Get the video ID.

        Raises:
            ValueError: If the video ID is not set.

        Returns:
            str: The video ID.

        """
        if self._video_id is None:
            logger.error("Video ID is not set, call set_video_id() first")
            raise ValueError("Video ID is not set, call set_video_id() first")
        return self._video_id

    @property
    def cache_dir_path(self) -> Path:
        """Get the path of the cache directory.

        Returns:
            Path: The path of the cache directory.

        """
        return self._root_path / "cache"

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
    def transcription_file_path(self) -> Path:
        """Get the path of the transcription file.

        Returns:
            Path: The path of the transcription file.

        """
        return self.video_dir_path / "transcription.txt"

    @property
    def resume_file_path(self) -> Path:
        """Get the path of the resume file.

        Returns:
            Path: The path of the resume file.

        """
        return self.video_dir_path / "resume.md"

    @property
    def metadata_file_path(self) -> Path:
        """Get the path of the metadata file.

        Returns:
            Path: The path of the metadata file.

        """
        return self.video_dir_path / "metadata.json"
