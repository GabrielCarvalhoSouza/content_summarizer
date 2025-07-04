"""Data models for the content summarizer.

This module provides data models for the content summarizer.

Classes:
    VideoMetadata: A data class for video metadata.
"""

from dataclasses import dataclass


@dataclass
class VideoMetadata:
    """Data class for video metadata."""

    id: str
    url: str
    title: str
    author: str
