"""Defines the command-line interface for the application.

This module uses the argparse library to build the entire CLI, including
commands, sub-commands, and all their respective arguments and options.
It is the main entry point for user interaction.

"""

import argparse
from pathlib import Path

WHISPER_MODEL_LIST = [
    "tiny",
    "base",
    "small",
    "medium",
    "large",
    "large-v2",
]

GEMINI_MODEL_LIST = [
    "1.0-pro",
    "1.5-flash",
    "1.5-pro",
    "2.5-flash",
    "2.5-pro",
]

DEVICES_LIST = [
    "cuda",
    "mps",
    "cpu",
    "auto",
]


def parse_arguments() -> argparse.Namespace:
    """Set up and parse all command-line arguments.

    Builds the complete CLI structure, defining the main parser,
    the 'summarize' and 'config' subparsers, and all their options.

    Returns:
        Namespace: An object containing the parsed command-line arguments.

    """
    parser = argparse.ArgumentParser(
        prog="content-summarizer",
        description="A tool to summarize YouTube videos.",
        epilog=(
            "Example: content-summarizer summarize "
            "https://youtu.be/jNQXAC9IVRw?si=d_6O-o9B5Lv8ShI5 --q"
        ),
    )

    subparsers = parser.add_subparsers(dest="command")

    parser_summarize = subparsers.add_parser(
        "summarize",
        help="Summarize a YouTube video from a given URL.",
    )

    parser_summarize.add_argument("url", type=str, help="The URL of the YouTube video.")

    parser_summarize.add_argument(
        "-o",
        "--output-path",
        type=Path,
        help="Specify a custom directory for output files.",
    )

    parser_summarize.add_argument(
        "-c",
        "--keep-cache",
        action="store_true",
        help="Prevent the deletion of cache files after execution.",
    )

    parser_summarize.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="Decrease console verbosity. Use -q for warnings/errors, -qq for silent.",
    )

    parser_summarize.add_argument(
        "-s",
        "--speed-factor",
        type=float,
        help="Specify the audio speed factor for acceleration (e.g., 1.5).",
    )

    parser_summarize.add_argument(
        "-a",
        "--api",
        action="store_true",
        help="Use a remote API for transcription instead of local processing.",
    )

    parser_summarize.add_argument(
        "--api-url",
        type=str,
        help="Specify the URL of the remote transcription API.",
    )

    parser_summarize.add_argument(
        "--api-key",
        type=str,
        help="Specify the API key for the remote transcription API.",
    )

    parser_summarize.add_argument(
        "--gemini-key",
        type=str,
        help="Specify the Google AI Studio API key.",
    )

    parser_summarize.add_argument(
        "-g",
        "--gemini-model",
        type=str,
        choices=GEMINI_MODEL_LIST,
        help="Specify the Gemini model to use for summarization.",
    )

    parser_summarize.add_argument(
        "-w",
        "--whisper-model",
        type=str,
        choices=WHISPER_MODEL_LIST,
        help="Specify the Whisper model for local transcription.",
    )

    parser_summarize.add_argument(
        "-b",
        "--beam-size",
        type=int,
        help="Specify the beam size for local Whisper transcription.",
    )

    parser_summarize.add_argument(
        "--device",
        type=str,
        choices=DEVICES_LIST,
        help="Specify the device for local transcription",
    )

    parser_summarize.add_argument(
        "--no-terminal",
        action="store_true",
        help="Disable printing the final summary to the terminal.",
    )

    parser_config = subparsers.add_parser(
        "config",
        help="Specify the default configuration values.",
    )

    parser_config.add_argument(
        "-o",
        "--output-path",
        type=Path,
        help="Specify the default custom directory for output files.",
    )

    parser_config.add_argument(
        "-s",
        "--speed-factor",
        type=float,
        help="Specify the default audio speed factor for acceleration (e.g., 1.5).",
    )

    parser_config.add_argument(
        "--api-url",
        type=str,
        help="Specify the default URL of the remote transcription API.",
    )

    parser_config.add_argument(
        "--api-key",
        type=str,
        help="Specify the default API key for the remote transcription API.",
    )

    parser_config.add_argument(
        "--gemini-key",
        type=str,
        help="Specify the default Google AI Studio API key.",
    )

    parser_config.add_argument(
        "-g",
        "--gemini-model",
        type=str,
        choices=GEMINI_MODEL_LIST,
        help="Specify the default Gemini model to use for summarization.",
    )

    parser_config.add_argument(
        "-w",
        "--whisper-model",
        type=str,
        choices=WHISPER_MODEL_LIST,
        help="Specify the default Whisper model for local transcription.",
    )

    parser_config.add_argument(
        "-b",
        "--beam-size",
        type=int,
        help="Specify the default beam size for local Whisper transcription.",
    )

    parser_config.add_argument(
        "--device",
        type=str,
        choices=DEVICES_LIST,
        help="Specify the default device for local transcription",
    )

    return parser.parse_args()
