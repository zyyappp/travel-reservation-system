from helpers.selection_helper import select
from helpers.login_helper import login_user, manage_accounts
from features.hotel import reserve_hotel
from features.car import reserve_car
from features.city import switch_city
from features.attractions import reserve_attraction
from features.payment import payment
from helpers.cli_helper import clear
#backlog: reset reservations if want to switch city
user = login_user()

def menu_interface():
    global user
    menu_options = ["Hotels", "Cars", "Attractions", "Payment", "Switch City", "Manage Accounts", "Quit"]
    menu = True

    redirect = {
        "Hotels" : reserve_hotel,
        "Cars" : reserve_car,
        "Attractions" : reserve_attraction,
        "Payment" : payment,
        "Switch City" : switch_city,
        "Manage Accounts" : manage_accounts
    }
    while menu:
        clear()
        print(f"Logged as {user.user}\nCity selected: {user.city}")
        try:
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
            elif redirect[user_input] is not None:
                redirect[user_input](user.id)
                continue
        except KeyboardInterrupt:
            continue



menu_interface()