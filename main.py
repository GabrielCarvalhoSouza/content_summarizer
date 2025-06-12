from cache import create_cache
from path_manager import path_manager
from resume import resume
from transcribe import transcribe
from youtube_service import youtube_service


def main():
    url = "https://youtu.be/ttzsxHVp2Aw?si=oHhRgnsNdbD57Mzi"

    youtube_service.get_youtube(url)

    path_manager.set_video_id(youtube_service.yt.video_id)

    create_cache(url)

    youtube_service.audio_download()

    transcribe()

    resume()


if __name__ == "__main__":
    main()
