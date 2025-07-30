import argparse
import locale
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.generative_models import GenerativeModel

from .audio_processor import AudioProcessor
from .cache_manager import CacheManager
from .config_manager import ConfigManager
from .data_models import VideoMetadata
from .path_manager import PathManager
from .summary_service import generate_summary
from .transcription_service import fetch_transcription_api, fetch_transcription_local
from .youtube_service import YoutubeService


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
    config_manager: ConfigManager
    gemini_model: GenerativeModel
    url: str
    output_path: Path
    keep_cache: bool
    quiet: int
    speed_factor: float
    api: bool
    api_url: str | None
    api_key: str | None
    gemini_key: str | None
    gemini_model_name: str
    whisper_model: str
    beam_size: int
    device: str
    user_language: str


def _resolve_config(
    args: argparse.Namespace, path_manager: PathManager, config_manager: ConfigManager
) -> dict[str, Any]:
    final_config: dict[str, Any] = {
        "output_path": path_manager.cache_dir_path,
        "keep_cache": False,
        "quiet": 0,
        "speed_factor": 1.25,
        "api": False,
        "api_url": "",
        "api_key": "",
        "gemini_key": "",
        "gemini_model": "2.5-flash",
        "whisper_model": "base",
        "beam_size": 5,
        "device": "auto",
    }

    user_saved_config: dict[str, Any] = config_manager.load_config()

    final_config.update(user_saved_config)

    load_dotenv(path_manager.parent_path / ".env")
    gemini_key: str | None = os.getenv("GEMINI_API_KEY")
    api_url: str | None = os.getenv("API_URL")
    api_key: str | None = os.getenv("TRANSCRIPTION_API_KEY")

    if gemini_key:
        final_config["gemini_key"] = gemini_key
    if api_url:
        final_config["api_url"] = api_url
    if api_key:
        final_config["api_key"] = api_key

    dict_args = vars(args)
    for key, value in dict_args.items():
        if value is None:
            continue
        if key == "command":
            continue
        final_config[key] = value

    return final_config


def _check_required_config_params(
    final_config: dict[str, Any], logger: logging.Logger
) -> None:
    if final_config["gemini_key"] == "":
        logger.exception("Gemini API key is required.")
        raise ValueError("Gemini API key is required.")

    if not final_config["api"]:
        return

    if not final_config["api_url"]:
        logger.exception("API URL is required when API mode is enabled.")
        raise ValueError("API URL is required when API mode is enabled.")

    if not final_config["api_key"]:
        logger.exception("API key is required when API mode is enabled.")
        raise ValueError("API key is required when API mode is enabled.")


def _get_user_system_language(logger: logging.Logger) -> str:
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

    return lang_code.split(".")[0].replace("_", "-")


def build_app_config(
    args: argparse.Namespace, logger: logging.Logger, path_manager: PathManager
) -> AppConfig:
    """Initialize all services, configurations, and dependencies.

    This function sets up logging, loads environment variables from a .env file,
    normalizes the user's system locale to a web-compatible format, and
    instantiates all necessary service classes.

    Returns:
        AppConfig: A populated dataclass instance with all dependencies.

    Raises:
        ValueError: If a required environment variable is not set.

    """
    GEMINI_MODEL_MAP = {
        "1.0-pro": "models/gemini-1.0-pro",
        "1.5-flash": "models/gemini-1.5-flash-latest",
        "1.5-pro": "models/gemini-1.5-pro-latest",
        "2.5-flash": "models/gemini-2.5-flash",
        "2.5-pro": "models/gemini-2.5-pro",
    }

    config_manager: ConfigManager = ConfigManager(path_manager.config_file_path)
    youtube_service: YoutubeService = YoutubeService()
    cache_manager: CacheManager = CacheManager()

    final_config: dict[str, Any] = _resolve_config(args, path_manager, config_manager)

    _check_required_config_params(final_config, logger)

    user_language: str = _get_user_system_language(logger)

    genai.configure(api_key=final_config["gemini_key"])
    gemini_model: GenerativeModel = genai.GenerativeModel(
        GEMINI_MODEL_MAP[final_config["gemini_model"]]
    )

    return AppConfig(
        logger=logger,
        path_manager=path_manager,
        youtube_service=youtube_service,
        cache_manager=cache_manager,
        config_manager=config_manager,
        gemini_model=gemini_model,
        url=final_config["url"],
        output_path=Path(final_config["output_path"]),
        keep_cache=final_config["keep_cache"],
        quiet=final_config["quiet"],
        speed_factor=final_config["speed"],
        api=final_config["api"],
        api_url=final_config["api_url"],
        api_key=final_config["api_key"],
        gemini_key=final_config["gemini_key"],
        gemini_model_name=final_config["gemini_model"],
        whisper_model=final_config["whisper_model"],
        beam_size=final_config["beam_size"],
        user_language=user_language,
        device=final_config["device"],
    )


def _save_caption(config: AppConfig, caption: str) -> None:
    """Execute the caption-based summary pipeline.

    This is the "fast path" workflow. It takes the pre-existing caption text,
    delegates saving it to the CacheManager, generates a summary from that
    file, and finally saves the summary.

    Args:
        config (AppConfig): The application configuration object.
        caption (str): The clean caption text to be processed.

    """
    config.cache_manager.save_text_file(caption, config.path_manager.caption_file_path)


def _save_accelerated_audio(config: AppConfig, accelerated_audio_path: Path) -> None:
    audio_processor: AudioProcessor = AudioProcessor(
        config.path_manager.audio_file_path, accelerated_audio_path
    )

    if not config.path_manager.audio_file_path.exists():
        config.youtube_service.audio_download(config.path_manager.audio_file_path)

    if not accelerated_audio_path.exists():
        audio_processor.accelerate_audio(config.speed_factor)


def _save_transcription(
    config: AppConfig, accelerated_audio_path: Path, transcription_file_path: Path
) -> None:
    if not transcription_file_path.exists():
        # Assert and default arguments are only for linter
        # It'll never be None because of _check_required_config_params()
        assert config.api_url is not None
        assert config.api_key is not None
        transcription_fetcher: dict[bool, Callable[[], str]] = {
            True: lambda url=config.api_url,
            key=config.api_key: fetch_transcription_api(
                url,
                accelerated_audio_path,
                key,
            ),
            False: lambda: fetch_transcription_local(
                accelerated_audio_path,
                config.whisper_model,
                config.beam_size,
                config.device,
            ),
        }

        selected_fetcher: Callable[[], str] = transcription_fetcher[config.api]
        transcription: str = selected_fetcher()

        if not transcription:
            raise PipelineError("Failed to fetch transcription")

        config.cache_manager.save_text_file(transcription, transcription_file_path)


def _prepare_source_file(config: AppConfig, caption: str | None) -> Path:
    if caption:
        config.logger.info("Manual caption found. Starting caption pipeline")
        _save_caption(config, caption)
        return config.path_manager.caption_file_path

    config.logger.info("No suitable caption found. Starting transcription pipeline")
    accelerated_audio_path: Path = config.path_manager.get_accelerated_audio_path(
        config.speed_factor
    )
    transcription_file_path: Path = config.path_manager.get_transcription_path(
        config.whisper_model, config.speed_factor, config.beam_size
    )
    _save_accelerated_audio(config, accelerated_audio_path)
    _save_transcription(config, accelerated_audio_path, transcription_file_path)

    return transcription_file_path


def summarize_video_pipeline(
    args: argparse.Namespace, logger: logging.Logger, path_manager: PathManager
) -> None:
    """Run the main application logic, acting as a dispatcher.

    This function initializes the configuration, loads video information,
    and then decides which pipeline to run (`caption_pipeline` or
    `transcription_pipeline`) based on the availability of manual captions.
    It contains the primary error handling for the application's workflow.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

    Raises:
        PipelineError: If an error occurs during the execution of a pipeline.
        SetupError: If an error occurs during the initial setup.

    """
    config: AppConfig | None = None
    try:
        config = build_app_config(args, logger, path_manager)
        config.youtube_service.load_from_url(config.url)
        config.path_manager.set_video_id(config.youtube_service.video_id)
    except Exception as e:
        logger.exception("An error occurred during the setup")
        raise SetupError(f"An error occurred during the setup: {e}") from e

    try:
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
            path_manager.metadata_file_path,
        )

        source_path = _prepare_source_file(config, caption)

        summary_file_path: Path = path_manager.get_summary_path(
            config.gemini_model_name,
            config.user_language,
            config.whisper_model,
            config.speed_factor,
            config.beam_size,
        )

        summary = generate_summary(
            config.gemini_model,
            config.user_language,
            source_path,
        )

        if summary:
            config.cache_manager.save_text_file(summary, summary_file_path)

    except Exception as e:
        config.logger.exception("An error occurred during the pipeline")
        raise PipelineError(f"An error occurred during the pipeline: {e}") from e


def handle_config_command(
    args: argparse.Namespace, logger: logging.Logger, path_manager: PathManager
) -> None:
    config_manager: ConfigManager = ConfigManager(path_manager.config_file_path)

    try:
        current_configs: dict[str, Any] = config_manager.load_config()
        dict_args: dict[str, Any] = vars(args)

        for key, value in dict_args.items():
            if value is None:
                continue
            if key == "command":
                continue
            if key == "output-path":
                current_configs[key] = str(value)
                continue
            current_configs[key] = value

        config_manager.save_config(current_configs)
        logger.info("Configuration saved successfully.")
    except OSError:
        logger.exception("Failed to save configuration.")
        raise
