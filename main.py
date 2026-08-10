import subprocess
import pandas as pd
from InquirerPy import inquirer
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
    city_data = pd.read_csv("malaysia_hotels.csv")
    subprocess.run("cls", shell=True)

    city = inquirer.fuzzy(
        message= f"--- Cities ---",
        choices = city_data[" cityName"].drop_duplicates(),
        height= 10
    ).execute()

    return city
    


def reserve_car():
    car_data = pd.read_csv("car_models.csv")
    subprocess.run("cls", shell=True)
    choice = inquirer.select(
        message=f"{"-" * 20}\nCars\n{"-" * 20}",
        choices = ["Full Criteria Search", "Based on Segment"]
    ).execute()

    city = select_city()

    if choice == "Full Criteria Search":
        # Full criteria includes brand, segment (specific)

        brand = inquirer.fuzzy(
            message= f"--- Car Brands ---",
            choices = car_data["Maker"].drop_duplicates(),
            height= 10
        ).execute()

        brand_segment = inquirer.fuzzy(
            message = f"--- Segments for {brand} ---",
            choices = car_data[car_data["Maker"] == brand]["Segment"].drop_duplicates(),
            height= 10
        ).execute()

        car_model = inquirer.fuzzy(
            message= f"--- Models for {brand} {brand_segment} ---",
            choices= car_data[(car_data["Maker"] == brand) & (car_data["Segment"] == brand_segment)]["Genmodel"].drop_duplicates(),
            height= 10
        ).execute()


    elif choice == "Based on Segment":
        #Includes segments, ignore brand
        segment = inquirer.fuzzy( 
            message= "--- Select Segment ---",
            choices = car_data["Segment"].drop_duplicates(),
            height= 10
        ).execute()

        segment_data = car_data[car_data["Segment"] == segment].drop_duplicates().reset_index(drop=True)

        choices = [
            f"{i+1}. " + " | ".join(str(value) for value in row)
            for i, row in segment_data.iterrows()
        ]
        car_series = inquirer.select( #Series object
            message= "-" * 20,
            choices= choices,
            height= 10
        ).execute()


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
        



menu_interface()