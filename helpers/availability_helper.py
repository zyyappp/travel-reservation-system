from config import hotel_data
from config import ROOM_AVAILABILITY_PATH
import json

def load_availability():
    with open(ROOM_AVAILABILITY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def dump_availability(info):
    with open(ROOM_AVAILABILITY_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)

def initialize_availability():
    available = load_availability()

    if not available:
        available = {hotel["HotelName"] : int(hotel["max_rooms"]) for _, hotel in hotel_data.iterrows()}
        dump_availability(available)

    return available