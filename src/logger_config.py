"""Custom logger configuration.

This module provides a custom logger configuration for the content summarizer.

Classes:
    CustomFormatter: A custom log formatter.

Functions:
    setup_logging: Set up logging.

"""

import logging
import sys

import colorlog


class CustomFormatter(colorlog.ColoredFormatter):
    """Custom log formatter.

    Attributes:
        simple_format (str): Format string for info level logs.
        detailed_format (str): Format string for non-info level logs.
        info_formatter (colorlog.ColoredFormatter): Formatter for info level logs.
        other_formatter (colorlog.ColoredFormatter): Formatter for non-info level logs.

    """

    def __init__(self) -> None:
        """Initialize the CustomFormatter."""
        super().__init__()
        self.simple_format = "%(message)s"
        self.detailed_format = "%(log_color)s%(levelname)s:%(reset)s %(message)s"
        self.info_formatter = colorlog.ColoredFormatter(self.simple_format)
        self.other_formatter = colorlog.ColoredFormatter(
            self.detailed_format,
            log_colors={"WARNING": "yellow", "ERROR": "red", "CRITICAL": "bold_red"},
        )

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record.

        """
        if record.levelname == "INFO":
            return self.info_formatter.format(record)
        return self.other_formatter.format(record)


def setup_logging() -> None:
    """Set up logging.

    This function initializes a logger with the following features:

        - Log level is set to INFO.
        - Log messages are sent to the console.
        - Log messages are formatted using a custom formatter.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    handler = colorlog.StreamHandler(sys.stdout)
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)
