"""Custom YouTube service configuration.

This module provides a custom YouTube service configuration for the content summarizer.

Classes:
    YoutubeService: A service that downloads audio from YouTube.
"""

import logging
from pathlib import Path
from typing import Self

from pytubefix import Stream, YouTube
from pytubefix.cli import on_progress

from .video_service_interface import BaseVideoService

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """An exception that raises if there is an error downloading audio from YouTube."""


class YoutubeService(BaseVideoService):
    """A service that downloads audio from YouTube.

    This class provides a method to download audio from YouTube by providing a URL.
    """

    def __init__(self) -> None:
        """Initialize the YouTube service."""
        self._yt: YouTube | None = None

    def load_from_url(self, source_url: str) -> Self:
        """Load a video from a URL.

        Args:
            source_url (str): The URL of the video to be loaded.

        Returns:
            Self: The instance of the YouTube service.

        """
        self._yt = YouTube(source_url, on_progress_callback=on_progress)
        logger.info("Loaded video: %s from URL: %s", self.title, source_url)
        return self

    @property
    def yt(self) -> YouTube:
        """Get the YouTube object.

        Raises:
            RuntimeError: If the video is not loaded.

        """
        if self._yt is None:
            logger.error("You must call load_from_url() first")
            raise RuntimeError("You must call load_from_url() first")
        return self._yt

    @property
    def video_id(self) -> str:
        """Get the video ID."""
        return self.yt.video_id

    @property
    def title(self) -> str:
        """Get the title of the video."""
        return self.yt.title

    @property
    def author(self) -> str:
        """Get the author of the video."""
        return self.yt.author

    def audio_download(self, audio_file_path: Path) -> None:
        """Download the audio file of the video.

        Args:
            audio_file_path (Path): The path of the audio file to be downloaded.

        Raises:
            DownloadError: If there is an error downloading the audio.

        """
        if audio_file_path.exists():
            logger.info("Audio file already exists, skipping download")
            return
        output_path: Path = audio_file_path.parent
        filename: str = audio_file_path.name
        try:
            ys: Stream | None = self.yt.streams.get_audio_only()
            if ys is None:
                logger.error("Audio stream not found")
                raise DownloadError("Audio stream not found")
            ys.download(output_path=str(output_path), filename=filename)
            logger.info("Audio downloaded successfully")
        except Exception as e:
            logger.exception(
                "Failed to download audio for video Id: %s, title: %s",
                self.video_id,
                self.title,
            )
            raise DownloadError(f"Failed to download audio: {e}") from e
