import json
from pathlib import Path


class CacheManager:
    def create_cache(
        self, url: str, video_id: str, title: str, author: str, metadata_file_path: Path
    ):
        metadata_file_path.parent.mkdir(parents=True, exist_ok=True)
        video_metadata = {
            "id": video_id,
            "title": title,
            "channel": author,
            "url": url,
        }
        with open(metadata_file_path, "w", encoding="utf-8") as f:
            json.dump(video_metadata, f, ensure_ascii=False, indent=4)
