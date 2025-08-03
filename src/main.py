"""Main entry point for the Content Summarizer application.

This module is responsible for initializing the application, parsing command-line
arguments, setting up logging, and dispatching tasks to the appropriate
core functions. It acts as the primary orchestrator and final error handler.

"""

import logging
import sys

from .cli import parse_arguments
from .core import handle_config_command, summarize_video_pipeline
from .logger_config import setup_logging
from .path_manager import PathManager
from .warning_config import setup_warnings


def main() -> None:
    """Run the main application logic.

    This function initializes all necessary components (warnings, args, logging),
    acts as a dispatcher to call the correct core function based on the
    user's command, and serves as the final safety net, catching any
    unhandled exceptions.

    """
    setup_warnings()
    args = parse_arguments()
    path_manager: PathManager = PathManager()

    quiet_level = getattr(args, "quiet", 0)

    setup_logging(path_manager.log_file_path, quiet_level)
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
