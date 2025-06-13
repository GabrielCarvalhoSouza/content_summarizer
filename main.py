import locale
import os

import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.generative_models import GenerativeModel

from cache_manager import CacheManager
from path_manager import PathManager
from resume_service import generate_summary
from transcription_service import fetch_transcription
from youtube_service import YoutubeService


def main() -> None:
    load_dotenv()
    api_key: str | None = os.getenv("GEMINI_API_KEY")
    api_url: str | None = os.getenv("API_URL")
    user_language: str | None
    user_language, _ = locale.getdefaultlocale()

    if api_key is None:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    if api_url is None:
        raise ValueError("API_URL environment variable not set")
    if user_language is None:
        user_language = "en"

    genai.configure(api_key=api_key)
    gemini_model: GenerativeModel = genai.GenerativeModel("models/gemini-2.0-flash")

    path_manager: PathManager = PathManager()
    youtube_service: YoutubeService = YoutubeService()
    cache_manager: CacheManager = CacheManager()
    url: str = "https://youtu.be/ttzsxHVp2Aw?si=oHhRgnsNdbD57Mzi"

    youtube_service.load_from_url(url)

    path_manager.set_video_id(youtube_service.video_id)

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

    fetch_transcription(
        api_url, path_manager.transcription_file_path, path_manager.audio_file_path
    )

    generate_summary(
        gemini_model,
        user_language,
        path_manager.transcription_file_path,
        path_manager.resume_file_path,
    )


if __name__ == "__main__":
    main()
