"""Defines the base interface for video services.

This module provides an abstract base class that ensures any video service
implementation will have a consistent set of methods and properties required
by the application's core logic.

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

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self


class BaseVideoService(ABC):
    """Abstract base class for video services.

    This class provides the interface for video services. It defines the basic
    methods and properties that a video service should have.

    Attributes:
        video_id: The ID of the video.
        title: The title of the video.
        author: The author of the video.

    """

    @abstractmethod
    def load_from_url(self, source_url: str) -> Self:
        """Load a video from a URL.

        Args:
            source_url: The URL of the video to be loaded.

        Returns:
            Self: The instance of the video service.

        """
        pass

    @property
    @abstractmethod
    def video_id(self) -> str:
        """Get the ID of the video.

        Returns:
            str: The ID of the video.

        """
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """Get the title of the video.

        Returns:
            str: The title of the video.

        """
        pass

    @property
    @abstractmethod
    def author(self) -> str:
        """Get the author of the video.

        Returns:
            str: The author of the video.

        """
        pass

    @abstractmethod
    def audio_download(self, audio_file_path: Path) -> None:
        """Download the audio file of the video.

        Args:
            audio_file_path: The path of the audio file to be downloaded.

        """
        pass
