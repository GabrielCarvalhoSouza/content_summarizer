import os
from pytubefix import YouTube, Stream
from pytubefix.cli import on_progress
from typing import cast

class YoutubeManager:
    def __init__(self):
        self._yt = None

    def get_youtube(self, url):
        self._yt = YouTube(url, on_progress_callback=on_progress)
        return self

    @property
    def yt(self):
        if self._yt is None:
            raise RuntimeError("YouTube não inicializado, chama get_youtube antes!")
        return self._yt

    def audio_already_exists(self):
        return os.path.exists(f"cache\\{self.yt.video_id}\\audio.mp3")

    def audio_download(self):
        if not self.audio_already_exists():
            ys = cast(Stream, self.yt.streams.get_audio_only())
            ys.download(output_path=f"cache\\{self.yt.video_id}", filename="audio.mp3")

manager = YoutubeManager()
