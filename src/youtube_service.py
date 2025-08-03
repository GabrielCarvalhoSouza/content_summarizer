"""Provides a service to interact with the YouTube platform.

This module implements the BaseVideoService interface for YouTube. It uses
the pytubefix library to handle video data extraction, audio downloading,
and caption fetching.
"""

import logging
from pathlib import Path
from typing import Self

from pytubefix import Stream, YouTube
from pytubefix.captions import Caption

from .video_service_interface import BaseVideoService

logger: logging.Logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Custom exception for errors during the YouTube audio download."""


class YoutubeService(BaseVideoService):
    """A service to download audio and fetch captions from YouTube.

    This class implements the BaseVideoService interface and provides methods
    to load a YouTube video, download its audio, and find the best captions.

    Attributes:
        _yt: An instance of the pytubefix.YouTube object, loaded via
            load_from_url().

    """

    def __init__(self) -> None:
        """Initialize the YouTube service."""
        self._yt: YouTube | None = None

    def load_from_url(self, source_url: str) -> Self:
        """Load a video from a URL.

        Args:
            source_url: The URL of the video to be loaded.

        Returns:
            The instance of the YouTube service.

        """
        self._yt = YouTube(source_url)
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
        """Download the highest quality audio-only stream to the specified path.

        This method downloads the highest quality audio-only stream from the
        video and saves it to the specified path.

        Args:
            audio_file_path (Path): The full path where the audio file will be saved.

        Raises:
            DownloadError: If no audio stream is found or if the download fails.

        """
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

    def find_best_captions(self, user_language: str) -> str | None:
        """Find the best available manual caption and returns its clean text.

        The search follows a specific hierarchy to ensure the best quality:
        1.  The user's specific language (e.g., 'pt-BR').
        2.  The user's generic language (e.g., 'pt').
        3.  English ('en') as a universal fallback.
        4.  Any other available manual caption as a last resort.

        Auto-generated captions are always ignored.

        Args:
            user_language: The user's preferred language code (e.g., 'pt-BR').

        Returns:
            The clean caption text if a manual caption is found, otherwise None.

        """
        if not self.yt.captions:
            logger.warning("No captions found for video")
            return None

        priority_codes = [user_language]
        if "-" in user_language:
            generic_language = user_language.split("-")[0]
            if generic_language not in priority_codes:
                priority_codes.append(generic_language)

        if "en" not in priority_codes:
            priority_codes.append("en")

        for code in priority_codes:
            caption: Caption | None = self.yt.captions.get(code)
            if caption is not None and not caption.code.startswith("a."):
                logger.info("Found manual caption in system language or English")
                return caption.generate_txt_captions()

        for caption in self.yt.captions:
            if not caption.code.startswith("a."):
                logger.warning("Found manual caption in any language")
                return caption.generate_txt_captions()
        logger.warning("No captions found for video")
        return None
