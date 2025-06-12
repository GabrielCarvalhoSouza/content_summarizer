import json
from pathlib import Path

from youtube_service import youtube_service


def create_cache(url):
    parent_path = Path(__file__).parent
    cache_dir_path = parent_path / "cache"
    video_dir_path = cache_dir_path / youtube_service.yt.video_id
    video_dir_path.mkdir(parents=True, exist_ok=True)
    json_path = video_dir_path / "metadata.json"
    video_metadata = {
        "id": youtube_service.yt.video_id,
        "title": youtube_service.yt.title,
        "channel": youtube_service.yt.author,
        "url": url,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(video_metadata, f, ensure_ascii=False, indent=4)
