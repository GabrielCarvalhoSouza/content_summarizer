from transcribe import transcribe
from youtube import manager
from resume import resume
from cache import create_cache

def main():
    url = "https://youtu.be/8Bzjm6OvBbs?si=oYgUT-Uh3t4Y1Ti5"
    manager.get_youtube(url)

    create_cache(url)

    manager.audio_download()

    transcribe()

    resume()

if __name__ == "__main__":
    main()

