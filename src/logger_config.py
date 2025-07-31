"""Custom logger configuration."""

import logging
import sys
from pathlib import Path

import colorlog


class CustomTerminalFormatter(colorlog.ColoredFormatter):
    """Custom log formatter for terminal output.

    This formatter displays INFO level logs as simple, clean messages without
    any prefix. Other levels (WARNING, ERROR, CRITICAL) are prefixed with their
    respective colored level names. It is designed to never display tracebacks
    in the console.

    Attributes:
        info_formatter (colorlog.ColoredFormatter): A specific formatter for INFO logs.

    """

    def __init__(self) -> None:
        """Initialize the CustomTerminalFormatter."""
        info_format = "%(message)s"
        other_format = "%(log_color)s%(levelname)s:%(reset)s %(message)s"
        super().__init__(
            fmt=other_format,
            log_colors={
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        self.info_formatter = colorlog.ColoredFormatter(info_format)

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record while ensuring tracebacks are suppressed.

        This method temporarily removes exception information from the log record
        before passing it to the parent formatter, guaranteeing that no traceback
        is ever printed to the console. The exception info is restored afterwards
        so that other handlers (like the file handler) can still access it.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The final formatted string for the console.

        """
        original_exc_info = record.exc_info
        original_exc_text = record.exc_text

        record.exc_info = None
        record.exc_text = None

        try:
            if record.levelno == logging.INFO:
                return self.info_formatter.format(record)
            return super().format(record)
        finally:
            record.exc_info = original_exc_info
            record.exc_text = original_exc_text


def setup_logging(log_file_path: Path, quiet: int) -> None:
    """Set up the application-wide logging with dual handlers.

    This function configures the root logger to send messages to two different
    handlers: one for the console with a clean, user-friendly format, and one
    for a file that exclusively logs tracebacks for debugging.

    Args:
        log_file_path (Path): The destination path for the error log file.
        quiet (int): A flag indicating whether to suppress console output.

    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    console_handler = colorlog.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    if quiet == 1:
        console_handler.setLevel(logging.WARNING)
    if quiet >= 2:
        console_handler.setLevel(100000)  # no logs
    console_handler.setFormatter(CustomTerminalFormatter())

    file_handler = logging.FileHandler(log_file_path, mode="w", encoding="utf-8")

    file_handler.setLevel(logging.INFO)

    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
