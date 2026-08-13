import subprocess
from config import DATA_FOLDER, RESERVES_PATH, city_data
import pandas as pd
from selection_helper import search
import json

def load_reserve():
    with open(RESERVES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def dump_reserve(info):
    with open(RESERVES_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)


def select_city(id):
    reserve_data = load_reserve()
    for data in reserve_data:
        if data["id"] == id:
            return data["city"]
        
    city = search("--- Cities ---", city_data[" cityName"].drop_duplicates())

    reserve_data.append(
        {
                "id" : id,
                "city" : city
        }
    )
    dump_reserve(reserve_data)
    return city

def switch_city(id):
    reserve_data = load_reserve()
    for data in reserve_data:
        if data["id"] == id:
            city = search("--- Cities ---", city_data[" cityName"].drop_duplicates())
            data["city"] = city

            dump_reserve(reserve_data)
            return city
    select_city(id)
