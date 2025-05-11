from transcribe import transcribe
from download import audio_download
from resume import resume

def main():
    audio_download("https://youtu.be/TucmVFrZptU?si=L6Wac4BEu6xOn-p_")

    transcribe()

    resume()
if __name__ == "__main__":
    main()

