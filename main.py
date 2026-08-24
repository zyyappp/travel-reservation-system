from helpers.selection_helper import select
from helpers.login_helper import login_user, manage_accounts
from features.hotel import reserve_hotel
from features.car import reserve_car
from features.city import switch_city
from features.attractions import reserve_attraction
from features.payment import payment
from features.reservations import reservations
from helpers.cli_helper import clear, print_header

user = login_user()

def menu_interface():
    global user
    menu_options = ["Reserve Hotel", "Reserve Car", "Reserve Attractions", "Reservations", "Payment", "Switch City", "Manage Accounts", "Help", "Quit"]
    menu = True

    redirect = {
        "Reserve Hotel": reserve_hotel,
        "Reserve Car": reserve_car,
        "Reserve Attractions": reserve_attraction,
        "Reservations" : reservations,
        "Payment": payment,
        "Switch City": switch_city,
        "Manage Accounts": manage_accounts,
        # "Help" is handled separately
    }
    while menu:
        clear()
        try:
            user_input = select(
                f"\n{'─'*60}\n        TRAVEL RESERVATION SYSTEM\n{'─'*60}\n\n"
                f"Logged in as: {user.user}\nCurrent city: {user.city}\n",
                menu_options
            )

            # Escape handling – go back to the menu without error
            if user_input == "BACK":
                continue

            if user_input == "Quit":
                clear()
                menu = False
                break

            if user_input == "Help":
                show_help()
                continue

            if user_input == "Switch City":
                user.city = switch_city(user.id)
                continue

            # Call the appropriate feature; if it returns a user object, update it
            result = redirect.get(user_input)
            if result:
                updated = result(user.id)
                if updated is not None:
                    user = updated
            continue
        except KeyboardInterrupt:
            continue



def show_help():
    clear()
    print_header("HELP")
    print("""
Help – What each option does:

Reserve Hotel      – Browse hotels and make a reservation.
Reserve Car        – Choose a car and reserve it.
Reserve Attraction – Pick attractions to visit.
Payment            – View/pay outstanding reservations.
Switch City        – Change your current city.
Manage Accounts    – Edit your user profile.
Help               – Show this help message.
Quit               – Exit the application.
""")
    input()

menu_interface()