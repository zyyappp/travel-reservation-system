
from config import RESERVES_PATH
import json

def load_reserve():
    with open(RESERVES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def dump_reserve(info):
    with open(RESERVES_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)
