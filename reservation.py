import subprocess
from config import DATA_FOLDER, RESERVES_PATH, city_data, car_data
import pandas as pd
from selection_helper import search, select
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
    return select_city(id)


def reserve_car(id):
    subprocess.run("cls", shell=True)

    choice = select(f"{"-" * 20}\nCars\n{"-" * 20}", ["Full Criteria Search", "Based on Segment"])

    if choice == "Full Criteria Search":
        # Full criteria includes brand, segment (specific)


        brand = search("--- Car Brands ---", car_data["Maker"].drop_duplicates())
        segment = search(f"--- Segments for {brand} ---", car_data[car_data["Maker"] == brand]["Segment"].drop_duplicates())

        car_model = search(f"--- Models for {brand} {segment} ---", car_data[(car_data["Maker"] == brand) & (car_data["Segment"] == segment)]["Genmodel"].drop_duplicates())

        car_price = float(car_data[(car_data["Maker"] == brand) & (car_data["Segment"] == segment) & (car_data["Genmodel"] == car_model)]["Rental_price"].to_list()[0])


    elif choice == "Based on Segment":
        #Includes segments, ignore brand
        segment = search("--- Select Segment ---", car_data["Segment"].drop_duplicates() )


        segment_data = car_data[car_data["Segment"] == segment].drop_duplicates().reset_index(drop=True)

        choices = [
            f"{i+1}. " + " | ".join(str(value) for value in row)
            for i, row in segment_data.iterrows()
        ]
        selected = select("--- Select Car ---", choices)

        selected_index = choices.index(selected)

        brand = segment_data.iloc[selected_index]["Maker"]
        car_model = segment_data.iloc[selected_index]["Genmodel"]
        car_price = float(segment_data.iloc[selected_index]["Rental_price"])

    car_details = f"""
{"-" * 20}
Brand : {brand}
Model : {car_model}
Segment : {segment}
Price : RM {car_price}
{"-" * 20}
"""
    print(car_details)

    reserve_data = load_reserve()

    for data in reserve_data:
        if data["id"] == id:
            if data.get("car") is None:
                data["car"] = []
                
            data["car"].append({
                "brand" : brand,
                "model" : car_model,
                "segment" : segment,
                "price" : car_price
            })

    dump_reserve(reserve_data)

    option = select("Enter option", ["Proceed to checkout", "Continue with another reservation", "Quit"])

    if option == "Continue with another reservation":
        return