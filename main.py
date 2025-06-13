import locale
import os

import google.generativeai as genai
from dotenv import load_dotenv

from cache_manager import CacheManager
from path_manager import PathManager
from resume_service import generate_summary
from transcription_service import fetch_transcription
from youtube_service import YoutubeService


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    api_url = os.getenv("API_URL")

    genai.configure(api_key=api_key)  # type: ignore[reportPrivateImportUsage]
    gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")  # type: ignore[reportPrivateImportUsage]

    path_manager = PathManager()
    youtube_service = YoutubeService()
    cache_manager = CacheManager()
    user_language, _ = locale.getdefaultlocale()
    url = "https://youtu.be/ttzsxHVp2Aw?si=oHhRgnsNdbD57Mzi"

    if api_key is None:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    if api_url is None:
        raise ValueError("API_URL environment variable not set")
    if user_language is None:
        raise ValueError("Default locale not found")

    youtube_service.get_youtube(url)

    path_manager.set_video_id(youtube_service.video_id)

    cache_manager.create_cache(
        url,
        path_manager.video_id,
        youtube_service.title,
        youtube_service.author,
        path_manager.metadata_file_path,
    )

    youtube_service.audio_download(
        path_manager.audio_file_path, path_manager.video_dir_path
    )

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
