import os
import json
import youtube
from youtube import manager

def create_cache():
    dictionary = {
        "id": manager.yt.video_id,
        "title": manager.yt.title
    }
    path = f"cache\\{manager.yt.video_id}"
    os.makedirs(path, exist_ok=True)
    path = f"cache\\{manager.yt.video_id}\\cache.json"
    with open(path, "w", encoding="utf-8") as f:
        cache = json.dump(dictionary, f, ensure_ascii=False, indent=4)