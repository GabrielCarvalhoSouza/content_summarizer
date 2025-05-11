import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
import json

def audio_already_exists():
    if os.path.exists("audios/audio.mp3"):
        return True
    return False

def audio_download(url):
    if not audio_already_exists():
        yt = YouTube(url, on_progress_callback=on_progress)
        ys = yt.streams.get_audio_only()
        ys.download(output_path="audios", filename="audio.mp3")

# def cache():
#     path = "cache\\{id}\\cache.json"
#     with open(path, "r", encoding="utf-8") as f:
#         cache = json.load(f)
#     return cache