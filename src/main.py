"""Main entry point for the content summarizer.

This module provides the main entry point for the content summarizer.

Functions:
    main: The main entry point for the content summarizer.

Classes:
    AppConfig: A data class for the application configuration.
    SetupError: An exception raised for errors in the setup process.
    PipelineError: An exception raised for errors during the pipeline execution.

Functions:
    setup: Set up the application configuration and environment variables.
    transcription_pipeline: The main pipeline for the content summarizer.
    run_application: Run the application with the provided URL.
    main: The main entry point for the content summarizer.
"""

import locale
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.generative_models import GenerativeModel

from .audio_processor import AudioProcessor
from .cache_manager import CacheManager
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
    """Configuration data class for the application."""

    logger: logging.Logger
    path_manager: PathManager
    api_key: str
    api_url: str
    transcription_api_key: str
    user_language: str
    speed_factor: float
    youtube_service: YoutubeService
    cache_manager: CacheManager
    gemini_model: GenerativeModel


def setup() -> AppConfig:
    """Set up the application configuration and environment variables."""
    setup_logging()
    logger = logging.getLogger(__name__)

    path_manager: PathManager = PathManager()

    load_dotenv(path_manager.parent_path / ".env")
    api_key: str | None = os.getenv("GEMINI_API_KEY")
    api_url: str | None = os.getenv("API_URL")
    transcription_api_key: str | None = os.getenv("TRANSCRIPTION_API_KEY")

    if api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("GEMINI_API_KEY environment variable not set")
    if api_url is None:
        logger.error("API_URL environment variable not set")
        raise ValueError("API_URL environment variable not set")
    if transcription_api_key is None:
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

    genai.configure(api_key=api_key)
    gemini_model: GenerativeModel = genai.GenerativeModel("models/gemini-2.5-flash")

    return AppConfig(
        logger=logger,
        path_manager=path_manager,
        api_key=api_key,
        api_url=api_url,
        transcription_api_key=transcription_api_key,
        user_language=user_language,
        speed_factor=speed_factor,
        youtube_service=youtube_service,
        cache_manager=cache_manager,
        gemini_model=gemini_model,
    )


def caption_pipeline(config: AppConfig, caption: str) -> None:
    """Execute the caption pipeline for a given URL."""
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
    """Execute the transcription pipeline for a given URL."""
    accelerated_audio_path: Path = config.path_manager.get_accelerated_audio_path(
        config.speed_factor
    )
    audio_processor: AudioProcessor = AudioProcessor(
        config.path_manager.audio_file_path, accelerated_audio_path
    )

    video_metadata: VideoMetadata = VideoMetadata(
        id=config.youtube_service.video_id,
        url=url,
        title=config.youtube_service.title,
        author=config.youtube_service.author,
    )

    config.cache_manager.save_metadata_file(
        video_metadata,
        config.path_manager.metadata_file_path,
    )

    if not config.path_manager.audio_file_path.exists():
        config.youtube_service.audio_download(config.path_manager.audio_file_path)

    if not accelerated_audio_path.exists():
        audio_processor.accelerate_audio(config.speed_factor)

    if not config.path_manager.transcription_file_path.exists():
        transcription = fetch_transcription(
            config.api_url,
            accelerated_audio_path,
            config.transcription_api_key,
        )
        if transcription:
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


def run_application(url: str) -> None:
    """Run the application with the provided URL."""
    config: AppConfig | None = None
    try:
        config = setup()
        config.youtube_service.load_from_url(url)
        config.path_manager.set_video_id(config.youtube_service.video_id)

        caption: str | None = config.youtube_service.find_best_captions(
            config.user_language
        )

        if caption:
            config.logger.info("Manual caption found. Starting caption pipeline")
            caption_pipeline(
                config,
                caption,
            )
            return
        config.logger.info("No suitable caption found. Starting transcription pipeline")
        transcription_pipeline(config, url)

    except Exception as e:
        if config:
            config.logger.exception("An error occurred during the pipeline")
            raise PipelineError(f"An error occurred during the pipeline: {e}") from e
        logging.exception("An error occurred during the setup")
        raise SetupError(f"An error occurred during the setup: {e}") from e


def main() -> None:
    """Initiate the application."""
    url: str = "https://youtu.be/y15070biffg?si=4i6IRg-qrqW-YOo4"

    try:
        run_application(url)
        logging.info("Application completed successfully.")
    except Exception:
        logging.critical("Fatal error occurred. Exiting application.")
        sys.exit(1)


if __name__ == "__main__":
    main()
