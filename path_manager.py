from pathlib import Path


class PathManager:
    def __init__(self):
        self.parent_path = Path(__file__).parent
        self._video_id = None

    def set_video_id(self, video_id: str):
        self._video_id = video_id
        return self

    @property
    def video_id(self):
        if self._video_id is None:
            raise ValueError("Video ID is not set, call set_video_id() first")
        return self._video_id

    @property
    def cache_dir_path(self):
        return self.parent_path / "cache"

    @property
    def video_dir_path(self):
        return self.cache_dir_path / self.video_id

    @property
    def audio_file_path(self):
        return self.video_dir_path / "audio.mp3"

    @property
    def transcription_file_path(self):
        return self.video_dir_path / "transcription.txt"

    @property
    def resume_file_path(self):
        return self.video_dir_path / "resume.md"

    @property
    def metadata_file_path(self):
        return self.video_dir_path / "metadata.json"
