from pathlib import Path
from typing import Self

from pytubefix import Stream, YouTube
from pytubefix.cli import on_progress

from .video_service_interface import BaseVideoService


class DownloadError(Exception):
    pass


class YoutubeService(BaseVideoService):
    def __init__(self) -> None:
        self._yt: YouTube | None = None

    def load_from_url(self, source_url: str) -> Self:
        self._yt = YouTube(source_url, on_progress_callback=on_progress)
        return self

    @property
    def yt(self) -> YouTube:
        if self._yt is None:
            raise RuntimeError("You must call load_from_url() first")
        return self._yt

    @property
    def video_id(self) -> str:
        return self.yt.video_id

    @property
    def title(self) -> str:
        return self.yt.title

    @property
    def author(self) -> str:
        return self.yt.author

    def audio_download(self, audio_file_path: Path) -> None:
        if audio_file_path.exists():
            return
        output_path: Path = audio_file_path.parent
        filename: str = audio_file_path.name
        try:
            ys: Stream | None = self.yt.streams.get_audio_only()
            if ys is None:
                raise DownloadError("Audio stream not found")
            ys.download(output_path=str(output_path), filename=filename)
        except Exception as e:
            raise DownloadError(f"Failed to download audio: {e}") from e
