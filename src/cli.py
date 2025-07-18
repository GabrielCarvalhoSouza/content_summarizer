"""Defines and parses command-line arguments for the application."""

import argparse
from pathlib import Path

GEMINI_MODEL_MAP = {
    "1.0-pro": "models/gemini-1.0-pro",
    "1.5-flash": "models/gemini-1.5-flash-latest",
    "1.5-pro": "models/gemini-1.5-pro-latest",
    "2.5-flash": "models/gemini-2.5-flash",
    "2.5-pro": "models/gemini-2.5-pro",
}

WHISPER_MODEL_LIST = [
    "tiny",
    "base",
    "small",
    "medium",
    "large",
    "large-v2",
]


def parse_arguments(cache_dir_path: Path) -> argparse.Namespace:
    """Set up the argument parser and parses the command-line arguments.

    This function builds the entire CLI structure, including the main parser and
    the 'summarize' and 'config' subparsers. It defines all the flags and
    options available to the user for both commands.

    Args:
        cache_dir_path (Path): The default path for the cache directory,
                               injected from the main application logic to be
                               used as a default for the '--output' flag.

    Returns:
        argparse.Namespace: An object containing the parsed command-line
                            arguments. The attributes of this object correspond
                            to the argument names.

    """
    parser = argparse.ArgumentParser(
        prog="content-summarizer",
        description="An cli program that summarizes youtube videos.",
        epilog="Example usage: content-summarizer https://youtu.be/jNQXAC9IVRw?si=d_6O-o9B5Lv8ShI5",
    )

    subparsers = parser.add_subparsers(dest="command")

    # Creation and configuration of the Summarize subparser
    parser_summarize = subparsers.add_parser(
        "summarize",
        help="Send an Youtube Url to be summarized.",
    )

    parser_summarize.add_argument("url", type=str, help="The URL of the YouTube video.")

    parser_summarize.add_argument(
        "-o",
        "--output",
        type=Path,
        default=cache_dir_path,
        help="The output directory.",
    )

    parser_summarize.add_argument(
        "-c",
        "--keep-cache",
        action="store_true",
        help="Keep the cache directory.",
    )

    parser_summarize.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="Increase logger level in the stderr",
    )

    parser_summarize.add_argument(
        "-s",
        "--speed",
        type=float,
        default=1.25,
        help="The speed factor for the audio. Default is 1.25.",
    )

    parser_summarize.add_argument(
        "-a",
        "--api",
        action="store_true",
        help="Use an API for whisper transcription instead of local.",
    )

    parser_summarize.add_argument(
        "--api-url",
        type=str,
        help="The URL of the API for whisper transcription.",
    )

    parser_summarize.add_argument(
        "--api-key",
        type=str,
        help="The key of the API for whisper transcription.",
    )

    parser_summarize.add_argument(
        "--gemini-key",
        type=str,
        help="The Gemini API key.",
    )

    parser_summarize.add_argument(
        "-g",
        "--gemini-model",
        type=str,
        choices=GEMINI_MODEL_MAP.keys(),
        default="2.5-flash",
        help="Set the Gemini model",
    )

    parser_summarize.add_argument(
        "-w",
        "--whisper-model",
        type=str,
        choices=WHISPER_MODEL_LIST,
        default="base",
        help="Set the Whisper model",
    )

    parser_summarize.add_argument(
        "-b", "--beam-size", type=int, default=5, help="The beam size for Whisper."
    )

    # Creation and configuration of the Summarize subparser
    parser_config = subparsers.add_parser(
        "config",
        help="Configure the default parameters for the application.",
    )

    parser_config.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Set the default output directory.",
    )

    parser_config.add_argument(
        "-s",
        "--speed",
        type=float,
        help="Set the default speed factor value.",
    )

    parser_config.add_argument(
        "--api-url",
        type=str,
        help="Set the default API URL.",
    )

    parser_config.add_argument(
        "--api-key",
        type=str,
        help="Set the default API key.",
    )

    parser_config.add_argument(
        "--gemini-key",
        type=str,
        help="Set the default Gemini API key.",
    )

    parser_config.add_argument(
        "-g",
        "--gemini-model",
        type=str,
        choices=GEMINI_MODEL_MAP.keys(),
        help="Set the default Gemini model.",
    )

    parser_config.add_argument(
        "-w",
        "--whisper-model",
        type=str,
        choices=WHISPER_MODEL_LIST,
        help="Set the default Whisper model.",
    )

    parser_config.add_argument(
        "-b",
        "--beam-size",
        type=int,
        help="Set the default Whisper beam size.",
    )

    return parser.parse_args()
