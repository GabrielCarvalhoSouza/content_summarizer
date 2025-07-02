import locale
import logging
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.generative_models import GenerativeModel

from .audio_processor import AudioProcessor
from .cache_manager import CacheManager
from .logger_config import setup_logging
from .path_manager import PathManager
from .summary_service import generate_summary
from .transcription_service import fetch_transcription
from .youtube_service import YoutubeService


def main() -> None:
    path_manager: PathManager = PathManager()
    load_dotenv(path_manager.parent_path / ".env")
    api_key: str | None = os.getenv("GEMINI_API_KEY")
    api_url: str | None = os.getenv("API_URL")
    transcription_api_key: str | None = os.getenv("TRANSCRIPTION_API_KEY")

    if api_key is None:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    if api_url is None:
        raise ValueError("API_URL environment variable not set")
    if transcription_api_key is None:
        raise ValueError("TRANSCRIPTION_API_KEY environment variable not set")

    setup_logging()
    logger = logging.getLogger(__name__)

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

    user_language = lang_code

    speed_factor: float = 1.25

    genai.configure(api_key=api_key)
    gemini_model: GenerativeModel = genai.GenerativeModel("models/gemini-2.5-flash")

    youtube_service: YoutubeService = YoutubeService()
    cache_manager: CacheManager = CacheManager()

    url: str = "https://www.youtube.com/watch?v=7w-UlP35UVA"

    youtube_service.load_from_url(url)

    path_manager.set_video_id(youtube_service.video_id)

    accelerated_audio_path: Path = path_manager.get_accelerated_audio_path(speed_factor)
    audio_processor: AudioProcessor = AudioProcessor(
        path_manager.audio_file_path, accelerated_audio_path
    )

    video_metadata: dict[str, str] = {
        "id": youtube_service.video_id,
        "title": youtube_service.title,
        "channel": youtube_service.author,
        "url": url,
    }

    cache_manager.create_cache(
        video_metadata,
        path_manager.metadata_file_path,
    )

    youtube_service.audio_download(path_manager.audio_file_path)

    audio_processor.accelerate_audio(speed_factor)

    fetch_transcription(
        api_url,
        path_manager.transcription_file_path,
        accelerated_audio_path,
        transcription_api_key,
    )

    generate_summary(
        gemini_model,
        user_language,
        path_manager.transcription_file_path,
        path_manager.summary_file_path,
    )


if __name__ == "__main__":
    main()
