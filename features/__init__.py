from config import RESERVES_PATH
import json

def dump_reserve(info):
    with open(RESERVES_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)

def load_reserve():
    try:
        with open(RESERVES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        dump_reserve([])
        return []