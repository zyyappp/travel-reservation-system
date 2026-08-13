import subprocess
import pandas as pd
import datetime
from selection_helper import select, search
from login_helper import login_user
from config import DATA_FOLDER, car_data, city_data
from user_class import User
from reservation import switch_city, reserve_car

def menu_interface():
    user = login_user()
    menu_options = ["Hotels", "Flights", "Trains", "Cars", "Attractions", "Payment", "AI Suggestion", "Switch City", "Quit"]
    menu = True

    redirect = {
        "Hotels" : None,
        "Flights" : None,
        "Trains" : None,
        "Cars" : reserve_car,
        "Attractions" : None,
        "Payment" : None,
        "AI Suggestion" : None,
        "Switch City" : switch_city
    }
    while menu:
        subprocess.run("cls", shell=True)
        print(f"Logged as {user.user}\nCity selected: {user.city}")
        user_input = select("", menu_options)

        if user_input == menu_options[-1]: 
            menu = False
            break
        elif user_input not in redirect.keys():
            continue
        elif user_input == "Switch City":
            user.city = switch_city(user.id)
            continue

        redirect[user_input](user.id)
        

menu_interface()