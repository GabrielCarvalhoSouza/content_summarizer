import os
import whisper


def transcription_already_exists():
    if os.path.exists("transcriptions/transcription.txt"):
        return True
    return False

def transcribe():
    if not transcription_already_exists():
        whisper_model = whisper.load_model("base")
        transcription = whisper_model.transcribe("audios/audio.mp3")
        with open("transcriptions/transcription.txt", "w", encoding="utf-8") as f:
            f.write(transcription["text"])
