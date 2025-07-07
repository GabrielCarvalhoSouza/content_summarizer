"""Custom cache manager configuration.

This module provides a custom cache manager configuration for the content summarizer.

Classes:
    CacheManager: A class to manage cache files for the content summarizer.

"""

import json
import logging
from dataclasses import asdict
from pathlib import Path

from .data_models import VideoMetadata

logger = logging.getLogger(__name__)


class CacheManager:
    """A class to manage cache files for the content summarizer."""

    def _write_to_file(self, content: str, file_path: Path) -> None:
        """Write content to a file.

        Args:
            content (str): The content to be written to the file.
            file_path (Path): The path of the file to be created.

        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with file_path.open("w", encoding="utf-8") as f:
                f.write(content)

            logger.info("File saved successfully to %s", file_path)
        except OSError:
            logger.exception("Failed to save file")
            raise

    def save_metadata_file(
        self, video_metadata: VideoMetadata, metadata_file_path: Path
    ) -> None:
        """Save a VideoMetadata object to a JSON file.

        Args:
            video_metadata (VideoMetadata): The VideoMetadata object to be saved.
            metadata_file_path (Path): The path of the JSON file to be created.

        """
        video_metadata_dict = asdict(video_metadata)
        json_content = json.dumps(video_metadata_dict, indent=4)

        self._write_to_file(json_content, metadata_file_path)

    def save_text_file(self, text: str, text_file_path: Path) -> None:
        """Save a text string to a file.

        Args:
            text (str): The text to be saved.
            text_file_path (Path): The path of the file to be created.

        """
        self._write_to_file(text, text_file_path)
