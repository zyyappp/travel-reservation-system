import subprocess
from config import BASE_DIR, DATA_FOLDER, car_data, city_data
import pandas as pd
import datetime
from helpers.selection_helper import select, search
from helpers.login_helper import login_user, switch_accounts
from user_class import User
from features.reservation import switch_city, reserve_car

def menu_interface():
    user = login_user()
    menu_options = ["Hotels", "Flights", "Trains", "Cars", "Attractions", "Payment", "AI Suggestion", "Switch City", "Switch Accounts", "Quit"]
    menu = True

    redirect = {
        "Hotels" : None,
        "Flights" : None,
        "Trains" : None,
        "Cars" : reserve_car,
        "Attractions" : None,
        "Payment" : None,
        "AI Suggestion" : None,
        "Switch City" : switch_city,
        "Switch Accounts" : switch_accounts
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
        elif user_input == menu_options[-3]:
            user.city = switch_city(user.id)
            continue
        elif user_input == menu_options[-2]:
            user = redirect[user_input](user.id)
            continue
        elif user_input == menu_options[3]:
            redirect[user_input](user.id)
            continue
        

menu_interface()