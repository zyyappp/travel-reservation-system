#module name  : __init__.py
#date created : 13th August 2026
#created by   : Yap Zi Yi
#imported     : config, json
#amendment    :
#remark       : Declare folder as module & loading & dumping jsons

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