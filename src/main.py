"""Main entry point and orchestrator for the Content Summarizer."""

import argparse
import locale
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.generative_models import GenerativeModel

from .audio_processor import AudioProcessor
from .cache_manager import CacheManager
from .cli import parse_arguments
from .config_manager import ConfigManager
from .data_models import VideoMetadata
from .logger_config import setup_logging
from .path_manager import PathManager
from .summary_service import generate_summary
from .transcription_service import fetch_transcription
from .youtube_service import YoutubeService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class SetupError(Exception):
    """Exception raised for errors in the setup process."""

    pass


class PipelineError(Exception):
    """Exception raised for errors during the pipeline execution."""

    pass


@dataclass
class AppConfig:
    """Holds all shared application configurations and service instances.

    This dataclass acts as a dependency injection container, making it easy to
    pass all necessary services and settings throughout the application.
    """

    logger: logging.Logger
    path_manager: PathManager
    youtube_service: YoutubeService
    cache_manager: CacheManager
    gemini_model: GenerativeModel
    url: str | None
    output_path: Path
    keep_cache: bool
    log_level: int
    speed_factor: float
    use_api: bool
    api_url: str | None
    api_key: str | None
    gemini_key: str | None
    gemini_model_name: str
    whisper_model: str
    beam_size: int
    user_language: str


def setup(args: argparse.Namespace) -> AppConfig:
    """Initialize all services, configurations, and dependencies.

    This function sets up logging, loads environment variables from a .env file,
    normalizes the user's system locale to a web-compatible format, and
    instantiates all necessary service classes.

    Returns:
        AppConfig: A populated dataclass instance with all dependencies.

    Raises:
        ValueError: If a required environment variable is not set.

    """
    path_manager: PathManager = PathManager()

    setup_logging(path_manager.log_file_path)
    logger: logging.Logger = logging.getLogger(__name__)

    load_dotenv(path_manager.parent_path / ".env")
    gemini_key: str | None = os.getenv("GEMINI_API_KEY")
    api_url: str | None = os.getenv("API_URL")
    api_key: str | None = os.getenv("TRANSCRIPTION_API_KEY")

    if gemini_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("GEMINI_API_KEY environment variable not set")
    if api_url is None:
        logger.error("API_URL environment variable not set")
        raise ValueError("API_URL environment variable not set")
    if api_key is None:
        logger.error("TRANSCRIPTION_API_KEY environment variable not set")
        raise ValueError("TRANSCRIPTION_API_KEY environment variable not set")

    DEFAULT_LOCALE: str = "en_US"
    lang_code: str | None

    try:
        locale.setlocale(locale.LC_ALL, "")
        lang_code, _ = locale.getlocale()
    except locale.Error:
        lang_code = None

    if not lang_code:
        logger.warning("Failed to detect locale, using default: %s", DEFAULT_LOCALE)
        lang_code = DEFAULT_LOCALE

    user_language = lang_code.split(".")[0].replace("_", "-")

    speed_factor: float = 1.25

    youtube_service: YoutubeService = YoutubeService()
    cache_manager: CacheManager = CacheManager()

    genai.configure(api_key=gemini_key)
    gemini_model: GenerativeModel = genai.GenerativeModel("models/gemini-2.5-flash")

    return AppConfig(
        logger,
        path_manager,
        youtube_service,
        cache_manager,
        gemini_model,
        args.url,
        args.output_path,
        args.keep_cache,
        args.log_level,
        speed_factor,
        args.use_api,
        api_url,
        api_key,
        gemini_key,
        args.gemini_model_name,
        args.whisper_model,
        args.beam_size,
        user_language,
    )


def caption_pipeline(config: AppConfig, caption: str) -> None:
    """Execute the caption-based summary pipeline.

    This is the "fast path" workflow. It takes the pre-existing caption text,
    delegates saving it to the CacheManager, generates a summary from that
    file, and finally saves the summary.

    Args:
        config (AppConfig): The application configuration object.
        caption (str): The clean caption text to be processed.

    """
    config.cache_manager.save_text_file(caption, config.path_manager.caption_file_path)
    summary = generate_summary(
        config.gemini_model,
        config.user_language,
        config.path_manager.caption_file_path,
    )

    if summary:
        config.cache_manager.save_text_file(
            summary, config.path_manager.summary_file_path
        )


def transcription_pipeline(config: AppConfig, url: str) -> None:
    """Execute the full transcription-based summary pipeline.

    This is the "slow path" workflow, used when no suitable captions are found.
    It orchestrates all necessary steps: audio download, acceleration,
    transcription via API, caching, and final summary generation.

    Args:
        config (AppConfig): The application configuration object.
        url (str): The URL of the YouTube video (passed for context, though unused).

    """
    accelerated_audio_path: Path = config.path_manager.get_accelerated_audio_path(
        config.speed_factor
    )
    audio_processor: AudioProcessor = AudioProcessor(
        config.path_manager.audio_file_path, accelerated_audio_path
    )

    if not config.path_manager.audio_file_path.exists():
        config.youtube_service.audio_download(config.path_manager.audio_file_path)

    if not accelerated_audio_path.exists():
        audio_processor.accelerate_audio(config.speed_factor)

    if not config.path_manager.transcription_file_path.exists():
        transcription = fetch_transcription(
            config.api_url,
            accelerated_audio_path,
            config.api_key,
        )
        config.cache_manager.save_text_file(
            transcription, config.path_manager.transcription_file_path
        )

    summary = generate_summary(
        config.gemini_model,
        config.user_language,
        config.path_manager.transcription_file_path,
    )

    if summary:
        config.cache_manager.save_text_file(
            summary, config.path_manager.summary_file_path
        )


def run_application(args: argparse.Namespace) -> None:
    """Run the main application logic, acting as a dispatcher.

    This function initializes the configuration, loads video information,
    and then decides which pipeline to run (`caption_pipeline` or
    `transcription_pipeline`) based on the availability of manual captions.
    It contains the primary error handling for the application's workflow.

    Args:
        url (str): The YouTube URL to be processed.

    Raises:
        PipelineError: If an error occurs during the execution of a pipeline.
        SetupError: If an error occurs during the initial setup.

    """
    config: AppConfig | None = None
    try:
        config = setup(args)
        config.youtube_service.load_from_url(config.url)
        config.path_manager.set_video_id(config.youtube_service.video_id)

        caption: str | None = config.youtube_service.find_best_captions(
            config.user_language
        )

        video_metadata: VideoMetadata = VideoMetadata(
            id=config.youtube_service.video_id,
            url=config.url,
            title=config.youtube_service.title,
            author=config.youtube_service.author,
        )

        config.cache_manager.save_metadata_file(
            video_metadata,
            config.path_manager.metadata_file_path,
        )

        if caption:
            config.logger.info("Manual caption found. Starting caption pipeline")
            caption_pipeline(config, caption)
            return

        config.logger.info("No suitable caption found. Starting transcription pipeline")
        transcription_pipeline(config, url)

    except Exception as e:
        if config:
            config.logger.exception("An error occurred during the pipeline")
            raise PipelineError(f"An error occurred during the pipeline: {e}") from e
        logging.exception("An error occurred during the setup")
        raise SetupError(f"An error occurred during the setup: {e}") from e


def handle_config_command(args: argparse.Namespace) -> None:
    path_manager: PathManager = PathManager()
    config_manager: ConfigManager = ConfigManager(path_manager.config_file_path)
    setup_logging(path_manager.log_file_path)
    logger: logging.Logger = logging.getLogger(__name__)

    try:
        current_configs: dict[str, Any] = config_manager.load_config()
        dict_args: dict[str, Any] = vars(args)

        for key, value in dict_args.items():
            if value is None:
                continue
            if key == "command":
                continue
            if key == "output":
                current_configs["output_path"] = str(value)
                continue
            current_configs[key] = value

        config_manager.save_config(current_configs)
        logger.info("Configuration saved successfully.")
    except OSError:
        logger.exception("Failed to save configuration.")
        raise


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
