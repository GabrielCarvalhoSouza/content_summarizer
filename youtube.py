import os
from pytubefix import YouTube
from pytubefix.cli import on_progress

class YoutubeManager:
    def __init__(self):
        self.yt = None

    def get_youtube(self, url):
        self.yt = YouTube(url, on_progress_callback=on_progress)
        return self

    def audio_already_exists(self):
        if os.path.exists("audios/audio.mp3"):
            return True
        return False

    def audio_download(self):
        if not self.audio_already_exists():
            ys = self.yt.streams.get_audio_only()
            ys.download(output_path="audios", filename="audio.mp3")

    def export_to_cache(self):
        attrs = ["video_id", "title"]
        return [getattr(self.yt, attr) for attr in attrs]

manager = YoutubeManager()