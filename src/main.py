"""Main entry point and orchestrator for the Content Summarizer."""

import logging
import sys

from .cli import parse_arguments
from .core import handle_config_command, summarize_video_pipeline
from .logger_config import setup_logging
from .path_manager import PathManager


def main() -> None:
    """Entry point for the application script.

    This function calls the core application logic and acts as the final
    safety net, catching any fatal exceptions, logging them, and setting the
    appropriate system exit code.
    """
    args = parse_arguments()
    path_manager: PathManager = PathManager()

    setup_logging(path_manager.log_file_path)
    logger: logging.Logger = logging.getLogger(__name__)
    try:
        if args.command == "config":
            handle_config_command(args, logger, path_manager)
            return
        summarize_video_pipeline(args, logger, path_manager)
        logger.info("Application completed successfully.")
    except Exception:
        logger.critical("Fatal error occurred. Exiting application.")
        sys.exit(1)


if __name__ == "__main__":
    main()
