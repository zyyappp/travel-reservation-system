import subprocess
from config import BASE_DIR, DATA_FOLDER, RESERVES_PATH, city_data, car_data
import pandas as pd
import os
os.chdir(BASE_DIR)
from helpers.selection_helper import search, select
from datetime import datetime, timedelta
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
        car_price = float(segment_data.iloc[selected_index]["Rental_price"]) #per day

    print(f"{"-" * 20}\nCar Rental Period\n{"-" * 20}")
    valid_date = False
    while not valid_date:
        try:
            start = datetime.strptime(input("Enter start date (DD/MM/YYYY) >> "), "%d/%m/%Y").date()
            end = datetime.strptime(input("Enter end date (DD/MM/YYYY) >> "), "%d/%m/%Y").date()

            if (datetime.now().date() - start).days > 0 or (datetime.now().date() - end).days > 0:
                print("Reservation date cannot be before the current date.")
                continue    
        except ValueError:
            print("Invalid date. Try again.")
            continue

        no_of_days = (end - start).days

        if no_of_days < 0:
            print("End date cannot be earlier than the start date.")
            continue
        elif no_of_days == 0:
            print("Day difference cannot be 0")
            continue
        else:
            valid_date = True
            break
        

    car_details = f"""
{"-" * 20}
Brand : {brand}
Model : {car_model}
Segment : {segment}
Price : RM {car_price}
Start date : {start}
End date: {end}
Days : {no_of_days}

{"-" * 20}
"""
    print(car_details)
    confirm = select("Confirm reservation? >> ", ["Yes", "No"])
    if confirm == "Yes":
        print("Reserved!")
        reserve_data = load_reserve()

        for data in reserve_data:
            if data["id"] == id:
                if data.get("car") is None:
                    data["car"] = []
                    
                data["car"].append({
                    "brand" : brand,
                    "model" : car_model,
                    "segment" : segment,
                    "price" : car_price,
                    "start_date" : str(start),
                    "end_date" : str(end),
                    "days" : no_of_days
                })

        dump_reserve(reserve_data)
        options = ["Proceed to checkout", "Continue with another reservation", "Quit"]
        option = select("Enter option", options)

        if option == options[0]:
            return payment(id)
        elif option == options[1]:
            return
        elif option == option[2]:
            quit()


def payment(id):
    pass