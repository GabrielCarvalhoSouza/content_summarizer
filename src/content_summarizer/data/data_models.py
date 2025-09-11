"""Defines the data structures for the application.

This module contains the dataclasses used to structure and pass data
consistently between different services and managers, ensuring a clear
and stable data contract.
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

from dataclasses import dataclass


@dataclass
class VideoMetadata:
    """Represents the essential metadata of a video.

    Attributes:
        id: The unique identifier of the video (e.g., YouTube video ID).
        url: The original URL of the video.
        title: The title of the video.
        author: The creator or channel name of the video.
        keep_cache: Used to prevent cache deletion on further runs.

    """

    id: str
    url: str
    title: str
    author: str
    keep_cache: bool
