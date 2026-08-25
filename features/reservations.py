from features import load_reserve, dump_reserve
from helpers.selection_helper import select, checkbox
from helpers.cli_helper import clear, print_header
from helpers.login_helper import load_login, dump_login


def get_city_reservations(data, city):
    return {
        key: [v for v in value if v["city"] == city]
        for key, value in data.items()
    }


def apply_filter(data, user_filter):
    if user_filter == "Default":
        return data

    if user_filter == "Hotel":
        return {"hotel": data["hotel"]}

    if user_filter == "Car":
        return {"car": data["car"]}

    if user_filter == "Attractions":
        return {"attractions": data["attractions"]}

    if user_filter == "Paid":
        return {
            key: [
                r for r in reservations
                if r["paid"] and not r["expired"]
            ]
            for key, reservations in data.items()
        }

    if user_filter == "Unpaid":
        return {
            key: [
                r for r in reservations
                if not r["paid"] and not r["expired"]
            ]
            for key, reservations in data.items()
        }

    if user_filter == "Expired":
        return {
            key: [
                r for r in reservations
                if r["expired"]
            ]
            for key, reservations in data.items()
        }

    return data


def print_reservations(data):

    prefixes = {
        "hotel": "night(s)",
        "car": "day(s)",
        "attractions": "pax",
    }

    if not any(data.values()):
        print("There are currently no reservations.")
        input()
        return False

    for reservation_type, reservations in data.items():

        if not reservations:
            continue

        print(f"""

{reservation_type.upper()}
{'─' * 60}
{"\n".join(
    f'{r["name"]}\n'
    f'{r["start"]} -> {r["end"]}\n'
    f'{r[prefixes[reservation_type].replace("(s)", "s")]} '
    f'{prefixes[reservation_type]} | '
    f'RM {r["net_total"]:.2f} | '
    f'{"PAID" if r["paid"] else "UNPAID"}'
    for r in reservations
)}
""")

    return True


def select_reservation(data):

    reservation_list = []

    for reservation_type, reservations in data.items():

        for reservation in reservations:

            reservation_list.append({
                "type": reservation_type,
                "reservation": reservation
            })

    choices = [
        f'{r["reservation"]["name"]} '
        f'({r["type"].capitalize()})'
        for r in reservation_list
    ]

    choices.append("Back")

    selected = select(
        "Select a reservation:",
        choices
    )

    if selected == "Back" or selected == "BACK":
        return None

    index = choices.index(selected)

    return reservation_list[index]


def print_reservation_details(reservation, reservation_type):

    prefixes = {
        "hotel": "night(s)",
        "car": "day(s)",
        "attractions": "pax",
    }

    value_key = prefixes[reservation_type].replace("(s)", "s")

    print(f"""
{'Name:':<20} {reservation["name"]}
{'City:':<20} {reservation["city"]}
{'Period':<20} {reservation["start"]} -> {reservation["end"]}
{value_key.capitalize() + ":":<20} {reservation[value_key]}
{'Payment:':<20} {"PAID" if reservation["paid"] else "UNPAID"}
{'Total:':<20} RM {reservation["net_total"]:.2f}

{'─' * 60}
""")


def reservations(user_id):

    current_page = "view"

    reservation_datas = load_reserve()
    user_login = load_login()

    account_login = next(
        data for data in user_login
        if data["id"] == user_id
    )

    account = next(
        data for data in reservation_datas
        if data["id"] == user_id
    )

    user_filter = account_login["reservations_filter"]

    city_reservations = get_city_reservations(
        account["reservations"],
        account["city"]
    )

    user_reservations = apply_filter(
        city_reservations,
        user_filter
    )

    while current_page != "finished":

        # RESERVATION MENU

        if current_page == "view":

            clear()

            ui_choices = [
                "View Reservations",
                "Change Filter",
                "Reset Filter",
                "Back"
            ]

            print_header("RESERVATIONS")
            print(f"Filter: {user_filter}")
            print(f"City: {account['city']}")

            reservation_ui = select("", ui_choices)

            if reservation_ui == "BACK" or reservation_ui == "Back":

                current_page = "finished"
                return

            elif reservation_ui == "View Reservations":

                current_page = "view_reservations"

            elif reservation_ui == "Change Filter":

                current_page = "change_filter"

            elif reservation_ui == "Reset Filter":

                current_page = "reset_filter"


        # VIEW RESERVATIONS

        if current_page == "view_reservations":

            clear()

            print_header("VIEW RESERVATIONS")

            valid = print_reservations(
                user_reservations
            )

            if not valid:

                current_page = "view"
                continue

            selected_reservation = select_reservation(
                user_reservations
            )

            if selected_reservation is None:

                current_page = "view"

            else:

                reservation = selected_reservation["reservation"]
                reservation_type = selected_reservation["type"]

                current_page = "reservation_details"


        # CHANGE FILTER

        if current_page == "change_filter":

            clear()

            print_header("SELECT FILTER")

            filters = [
                "Default",
                "Paid",
                "Unpaid",
                "Expired",
                "Hotel",
                "Car",
                "Attractions"
            ]

            new_filter = select(
                "Filter by:",
                filters + ["Back"]
            )

            if new_filter == "Back" or new_filter == "BACK":

                current_page = "view"
                continue

            user_filter = new_filter

            account_login["reservations_filter"] = user_filter

            dump_login(user_login)

            user_reservations = apply_filter(
                city_reservations,
                user_filter
            )

            current_page = "view"

        if current_page == "reset_filter":
            user_filter = account_login["reservations_filter"] = "Default"
            user_reservations = apply_filter(
                    city_reservations,
                    user_filter
                )

            dump_login(user_login)
            current_page = "view"
            


        # RESERVATION DETAILS

        if current_page == "reservation_details":

            clear()

            print_header("RESERVATION DETAILS")

            print_reservation_details(
                reservation,
                reservation_type
            )

            detail_choices = [
                "Cancel Reservation",
                "Back"
            ]

            detail_ui = select(
                "Select an option:",
                detail_choices
            )

            if detail_ui == "Cancel Reservation":

                current_page = "cancel_confirmation"

            elif detail_ui == "Back" or detail_ui == "BACK":

                current_page = "view_reservations"


        # CANCEL CONFIRMATION

        if current_page == "cancel_confirmation":

            clear()

            print_header("CANCEL RESERVATION")

            print(f"""
Reservation ID:  {reservation["reservation_id"]}
Name:            {reservation["name"]}
City:            {reservation["city"]}
Start:           {reservation["start"]}
End:             {reservation["end"]}
Total:           RM {reservation["net_total"]:.2f}
Payment:         {"PAID" if reservation["paid"] else "UNPAID"}

Are you sure you want to cancel this reservation?
""")

            confirm = select(
                "Select an option:",
                [
                    "Yes, cancel reservation",
                    "No, keep reservation"
                ]
            )

            if confirm == "Yes, cancel reservation":

                current_page = "cancel_reservation"

            else:

                current_page = "reservation_details"


        # CANCEL RESERVATION

        if current_page == "cancel_reservation":

            clear()

            print_header("CANCEL RESERVATION")

            for reservations_list in account["reservations"].values():

                if reservation in reservations_list:

                    reservations_list.remove(reservation)
                    break

            dump_reserve(reservation_datas)

            print("Reservation cancelled successfully! ✓")

            input("Press ENTER to return...\n")

            # Refresh reservations after deletion

            city_reservations = get_city_reservations(
                account["reservations"],
                account["city"]
            )

            user_reservations = apply_filter(
                city_reservations,
                user_filter
            )

            current_page = "view"