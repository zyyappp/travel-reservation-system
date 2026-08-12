import subprocess
import pandas as pd
import datetime
from selection_helper import select, search
from login_helper import login_user
from config import DATA_FOLDER

interface = f"""
{"-" * 20}
1. Hotels
2. Flights
3. Trains
4. Cars
5. Attractions
6. Payment
7. Quit
{"-" * 20}
            """

def select_city():
    city_data = pd.read_csv(DATA_FOLDER / "malaysia_hotels.csv")
    subprocess.run("cls", shell=True)
    city = search("--- Cities ---", city_data[" cityName"].drop_duplicates())

    return city
    


def reserve_car():
    car_data = pd.read_csv(DATA_FOLDER /"car_models.csv")
    subprocess.run("cls", shell=True)

    choice = select(f"{"-" * 20}\nCars\n{"-" * 20}", ["Full Criteria Search", "Based on Segment"])

    city = select_city()

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

    option = select("Enter option", ["Proceed to checkout", "Continue with another reservation", "Quit"])


def menu_interface():
    menu = True

    redirect = {
        "1" : None,
        "2" : None,
        "3" : None,
        "4" : reserve_car,
        "5" : None,
        "6" : None
    }
    while menu:
        subprocess.run("cls", shell=True)
        print(interface)
        user_input = input("Option >> ").strip()

        if user_input == "7": 
            menu = False
            break
        elif user_input not in redirect.keys():
            continue
        
        return redirect[user_input]()
        


login_user()
menu_interface()