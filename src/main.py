"""Main entry point and orchestrator for the Content Summarizer."""

import logging
import sys

from .cli import parse_arguments
from .core import handle_config_command, run_application

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> None:
    """Entry point for the application script.

    This function calls the core application logic and acts as the final
    safety net, catching any fatal exceptions, logging them, and setting the
    appropriate system exit code.
    """
    args = parse_arguments()
    try:
        if args.command == "config":
            handle_config_command(args)
            return
        run_application(args)
        logging.info("Application completed successfully.")
    except Exception:
        logging.critical("Fatal error occurred. Exiting application.")
        sys.exit(1)


if __name__ == "__main__":
    main()
