from features import load_reserve, dump_reserve
from helpers.selection_helper import search
from config import hotel_data

def select_city(user_id):
    current_page = "city_selection"
    reserve_data = load_reserve()
    for data in reserve_data:
        if data["id"] == user_id:
            return data["city"]

    while current_page != "finished":
        city = search("--- Cities ---", hotel_data["cityName"].drop_duplicates())

        if city == "BACK":
            continue
        elif city is None:
            print("City not found. Try again")
            continue
        else:
            reserve_data.append(
                {
                        "id" : user_id,
                        "city" : city
                }
            )
            dump_reserve(reserve_data)
            current_page = "finished"
            return city

def switch_city(user_id):
    current_page = "switch_city"
    reserve_data = load_reserve()
    for data in reserve_data:
        if data["id"] == user_id:

            while current_page != "finished":
            
                city = search("--- Cities ---", hotel_data["cityName"].drop_duplicates())

                if city == "BACK":
                    current_page = "finished"
                    return data["city"]
                elif city is None:
                    print("City not found. Try again")
                    continue
                else:
                    data["city"] = city

                    dump_reserve(reserve_data)
                    current_page = "finished"
                    return city