from pathlib import Path
from typing import cast

from pytubefix import Stream, YouTube
from pytubefix.cli import on_progress


class DownloadError(Exception):
    pass


class YoutubeService:
    def __init__(self):
        self._yt: YouTube | None = None

    def get_youtube(self, url: str):
        self._yt = YouTube(url, on_progress_callback=on_progress)
        return self

    @property
    def yt(self):
        if self._yt is None:
            raise RuntimeError("You must call get_youtube() first")
        return self._yt

    @property
    def video_id(self):
        return self.yt.video_id

    @property
    def title(self):
        return self.yt.title

    @property
    def author(self):
        return self.yt.author

    def audio_download(self, audio_file_path: Path, video_dir_path: Path):
        if audio_file_path.exists():
            return
        try:
            ys = cast(Stream, self.yt.streams.get_audio_only())
            if ys is None:
                raise DownloadError("Audio stream not found")
            ys.download(output_path=str(video_dir_path), filename="audio.mp3")
        except Exception as e:
            raise DownloadError(f"Failed to download audio: {e}") from e
