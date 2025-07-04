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

    def create_cache(
        self, video_metadata: VideoMetadata, metadata_file_path: Path
    ) -> None:
        """Create a cache file and a metadata file for the given video.

        Args:
            video_metadata (VideoMetadata): The metadata of the video.
            metadata_file_path (Path): The path of the metadata file to be created.

        """
        metadata_file_path.parent.mkdir(parents=True, exist_ok=True)

        video_metadata_dict = asdict(video_metadata)
        with metadata_file_path.open("w", encoding="utf-8") as f:
            json.dump(video_metadata_dict, f, ensure_ascii=False, indent=4)

        logger.info("Cache and metadata files created successfully")
