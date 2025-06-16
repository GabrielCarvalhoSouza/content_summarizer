import json
from pathlib import Path


class CacheManager:
    def create_cache(
        self, video_metadata: dict[str, str], metadata_file_path: Path
    ) -> None:
        metadata_file_path.parent.mkdir(parents=True, exist_ok=True)

        with metadata_file_path.open("w", encoding="utf-8") as f:
            json.dump(video_metadata, f, ensure_ascii=False, indent=4)
