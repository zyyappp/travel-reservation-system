from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from config import city_data, car_data

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
    return select_city(id)