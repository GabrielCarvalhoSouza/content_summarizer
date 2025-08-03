"""Defines the data structures for the application.

This module contains the dataclasses used to structure and pass data
consistently between different services and managers, ensuring a clear
and stable data contract.
"""

from dataclasses import dataclass


@dataclass
class VideoMetadata:
    """Represents the essential metadata of a video.

    Attributes:
        id: The unique identifier of the video (e.g., YouTube video ID).
        url: The original URL of the video.
        title: The title of the video.
        author: The creator or channel name of the video.

    """

    id: str
    url: str
    title: str
    author: str
