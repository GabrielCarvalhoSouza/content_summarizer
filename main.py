from transcribe import transcribe
from youtube import manager
from resume import resume
from cache import create_cache

def main():
    manager.get_youtube("https://www.youtube.com/watch?v=TucmVFrZptU")
    manager.audio_download()

    create_cache()
    #transcribe()

    #resume()
if __name__ == "__main__":
    main()

