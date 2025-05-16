import os
import whisper
from youtube import manager

def transcription_already_exists():
    if os.path.exists(f"cache\\{manager.yt.video_id}\\transcription.txt"):
        return True
    return False

def transcribe():
    if not transcription_already_exists():
        whisper_model = whisper.load_model("base")
        transcription = whisper_model.transcribe(f"cache\\{manager.yt.video_id}\\audio.mp3")
        with open(f"cache\\{manager.yt.video_id}\\transcription.txt", "w", encoding="utf-8") as f:
            f.write(transcription["text"])
