"""Provides a centralized class for managing all cache-related file operations."""

import json
import logging
from dataclasses import asdict
from pathlib import Path

from .data_models import VideoMetadata

logger: logging.Logger = logging.getLogger(__name__)


class CacheManager:
    """Handles writing and managing cache files for the application.

    This class abstracts file I/O operations, ensuring that all cache writes
    are handled consistently and robustly.
    """

    def _write_to_file(self, content: str, file_path: Path) -> None:
        """Private helper method to write text content to a specified file path.

        This method is the core of the cache writing logic, handling directory
        creation and OS-level errors.

        Args:
            content (str): The string content to be written to the file.
            file_path (Path): The destination file path.

        Raises:
            OSError: If the file cannot be written due to I/O or permission issues.

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
        """Serialize video metadata to JSON and saves it to a file.

        Args:
            video_metadata (VideoMetadata): The dataclass object containing video
                metadata.
            metadata_file_path (Path): The path for the 'metadata.json' file.

        """
        video_metadata_dict = asdict(video_metadata)
        json_content = json.dumps(video_metadata_dict, indent=4)

        self._write_to_file(json_content, metadata_file_path)

    def save_text_file(self, text: str, text_file_path: Path) -> None:
        """Save a plain text string to a specified file path.

        Args:
            text (str): The text content to save.
            text_file_path (Path): The destination file path (e.g., for captions or
                summaries).

        """
        self._write_to_file(text, text_file_path)
