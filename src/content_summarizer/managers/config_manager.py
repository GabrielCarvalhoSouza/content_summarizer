"""Manages the application's persistent configuration.

This module provides a class to handle reading from and writing to the
user's configuration file (config.json), abstracting file I/O operations
and error handling away from the core application logic.

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

import json
import logging
from pathlib import Path
from typing import Any

logger: logging.Logger = logging.getLogger(__name__)


class ConfigManager:
    """Handles reading and writing the user's configuration file.

    Attributes:
        _config_file: The path to the configuration file.

    """

    def __init__(self, config_file_path: Path) -> None:
        """Initialize the ConfigManager.

        Args:
            config_file_path: The path to the configuration file.

        """
        self._config_file = config_file_path

    def load_config(self) -> dict[str, Any]:
        """Load configurations from the config.json file.

        Reads the JSON configuration file. If the file does not exist
        or contains invalid JSON, it safely returns an empty dictionary.

        Returns:
            A dictionary containing the user's saved configurations, or an
            empty dictionary if an error occurs.

        """
        if not self._config_file.is_file():
            logger.info(
                "Configuration file not found. "
                "The application will run with its internal settings."
            )
            return {}

        try:
            with self._config_file.open("r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(
                "Configuration file is corrupted or invalid. "
                "The application will run with its internal settings instead."
            )
            return {}

    def save_config(self, config_data: dict[str, Any]) -> None:
        """Save a dictionary of configurations to the config.json file.

        This method serializes the provided dictionary to JSON and writes it
        to the configuration file, overwriting any existing content. It also
        ensures that the parent directory exists before writing.

        Args:
            config_data: A dictionary containing the configurations
                                to be saved.

        Raises:
            OSError: If the file cannot be written due to I/O or permission issues.

        """
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with self._config_file.open("w") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
        except OSError:
            logger.exception("Failed to save config file")
            raise
