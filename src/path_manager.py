from pathlib import Path
from typing import Self


class PathManager:
    def __init__(self) -> None:
        self._parent_path: Path = Path(__file__).parent
        self._root_path: Path = self._parent_path.parent
        self._video_id: str | None = None

    def set_video_id(self, video_id: str) -> Self:
        self._video_id = video_id
        return self

    @property
    def video_id(self) -> str:
        if self._video_id is None:
            raise ValueError("Video ID is not set, call set_video_id() first")
        return self._video_id

    @property
    def cache_dir_path(self) -> Path:
        return self._root_path / "cache"

    @property
    def video_dir_path(self) -> Path:
        return self.cache_dir_path / self.video_id

    @property
    def audio_file_path(self) -> Path:
        return self.video_dir_path / "audio.mp3"

    @property
    def transcription_file_path(self) -> Path:
        return self.video_dir_path / "transcription.txt"

    @property
    def resume_file_path(self) -> Path:
        return self.video_dir_path / "resume.md"

    @property
    def metadata_file_path(self) -> Path:
        return self.video_dir_path / "metadata.json"
