from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self


class BaseVideoService(ABC):
    @abstractmethod
    def load_from_url(self, source_url: str) -> Self:
        pass

    @property
    @abstractmethod
    def video_id(self) -> str:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def author(self) -> str:
        pass

    @abstractmethod
    def audio_download(self, audio_file_path: Path) -> None:
        pass
