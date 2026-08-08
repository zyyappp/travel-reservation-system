import subprocess
import pandas as pd
import time
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
    data = pd.read_csv("worldcities.csv")
    countries = data["country"].drop_duplicates()
    subprocess.run("cls", shell=True)
    country = inquirer.fuzzy(
        message="--- Countries ---",
        choices =  countries.sort_values().tolist(),
        height = 10
    ).execute()

    cities = inquirer.fuzzy(
        message= f"--- Cities in {country} ---",
        choices = data[data["country"] == country]["city"],
        height= 10
    ).execute()

    print("You selected %s" %cities)
    


def reserve_car():
    select_city()

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
            print("Invalid choice")
            time.sleep(1)
            continue
        
        return redirect[user_input]()
        



menu_interface()