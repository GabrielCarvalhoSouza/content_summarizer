import os
import json
import youtube
from youtube import manager

def create_cache():
    data = manager.export_to_cache()
    id = data[0]
    title = data[1]
    dictionary = {
        "id": id,
        "title": title
    }
    path = f"cache\\{id}"
    os.makedirs(path, exist_ok=True)
    path = f"cache\\{id}\\cache.json"
    with open(path, "w", encoding="utf-8") as f:
        cache = json.dump(dictionary, f, ensure_ascii=False, indent=4)