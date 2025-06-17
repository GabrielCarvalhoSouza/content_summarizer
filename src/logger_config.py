import logging
import sys

import colorlog


class CustomFormatter(colorlog.ColoredFormatter):
    def __init__(self) -> None:
        self.simple_format = "%(message)s"
        self.detailed_format = "%(log_color)s%(levelname)s:%(reset)s %(message)s"
        super().__init__()
        self.info_formatter = colorlog.ColoredFormatter(self.simple_format)
        self.other_formatter = colorlog.ColoredFormatter(
            self.detailed_format,
            log_colors={"WARNING": "yellow", "ERROR": "red", "CRITICAL": "bold_red"},
        )

    def format(self, record: logging.LogRecord) -> str:
        if record.levelname == "INFO":
            return self.info_formatter.format(record)
        return self.other_formatter.format(record)


def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    handler = colorlog.StreamHandler(sys.stdout)
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)
