"""Provides a centralized class for managing all config-related file operations."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """Handles reading and writing the user's configuration file."""

    def __init__(self, config_dir_path: Path) -> None:
        """Initialize the ConfigManager.

        Args:
            config_dir_path (Path): The path to the directory where the
                                    configuration file is stored.

        """
        self._config_file = config_dir_path / "config.json"

    def load_config(self) -> dict[str, Any]:
        """Load configurations from the config.json file.

        This method reads the JSON configuration file. If the file does not
        exist or contains invalid JSON, it safely returns an empty dictionary.

        Returns:
            dict: A dictionary containing the user's saved configurations.

        """
        if self._config_file.is_file():
            try:
                with self._config_file.open("r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_config(self, config_data: dict[str, Any]) -> None:
        """Save a dictionary of configurations to the config.json file.

        This method serializes the provided dictionary to JSON and writes it
        to the configuration file, overwriting any existing content. It also
        ensures that the parent directory exists before writing.

        Args:
            config_data (dict): A dictionary containing the configurations
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
