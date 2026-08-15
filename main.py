import subprocess
from helpers.selection_helper import select, search
from helpers.login_helper import login_user, switch_accounts
from features.hotel import reserve_hotel
from features.car import reserve_car
from features.city import switch_city
from features.attraction import reserve_attraction
from helpers.cli_helper import clear

def menu_interface():
    user = login_user()
    menu_options = ["Hotels", "Trains", "Cars", "Attractions", "Payment", "AI Suggestion", "Switch City", "Manage Accounts", "Quit"]
    menu = True

    redirect = {
        "Hotels" : reserve_hotel,
        "Trains" : None,
        "Cars" : reserve_car,
        "Attractions" : reserve_attraction,
        "Payment" : None,
        "Switch City" : switch_city,
        "Manage Accounts" : switch_accounts
    }
    while menu:
        clear()
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
        else:
            redirect[user_input](user.id)
            continue
        

menu_interface()