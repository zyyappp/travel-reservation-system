#module name  : attractions.py
#date created : 19th August 2026
#created by   : Yap Zi Yi
#imported     : features, helpers.login_helper, helpers.selection_helper, helpers.cli_helper, config, datetime, features.payment, time
#amendment    :
#remark       : Attractions Reservations 
from features import load_reserve, dump_reserve
from helpers.login_helper import load_login, dump_login
from helpers.selection_helper import search, select
from helpers.cli_helper import clear, print_header
from config import attraction_data
from datetime import datetime
from features.payment import payment
import time

def apply_filter(data, city, user_filter):
    # Takes the attraction data, selected city and user's filter.
    # Filters attractions by city and according to the selected filter.
    # Returns the filtered attraction data.

    city_attractions = data[data["City"] == city]

    if user_filter == "Default":
        pass

    elif user_filter == "Price: Low → High":
        city_attractions = city_attractions.sort_values("Entry_Price_MYR")

    elif user_filter == "Price: High → Low":
        city_attractions = city_attractions.sort_values("Entry_Price_MYR", ascending = False)

    elif user_filter.startswith("Category: "):
        category = user_filter.split(": ", 1)[1]
        city_attractions = city_attractions[city_attractions["Category"] == category]

    return city_attractions.reset_index(drop=True)


def select_attraction(city_attractions, city):
    # Displays attractions available in the selected city.
    # Returns the selected attraction or None if the user goes back.

    print_header(f"ATTRACTIONS IN {city.upper()}")

    if city_attractions.empty:
        print("Oops! It seems that there are no attraction places in this city. Please try another city.")
        input()
        return None

    choices = [
        f"{f'{i+1}.':<5} {data['Name']:<50} | {data['Category']:<12} | RM {data['Entry_Price_MYR']:.2f}"
        for i, data in city_attractions.iterrows()
    ]

    user_attraction = search("", choices, 10)

    if user_attraction == "BACK":
        return None

    elif user_attraction is not None:
        choice_index = choices.index(user_attraction)
        return city_attractions.iloc[choice_index]

    return None


def select_attraction_dates():
    # Gets and validates the attraction reservation start and end dates.
    # Returns the reservation dates and number of days.

    print_header("ATTRACTION RESERVATION PERIOD")
    valid_date = False

    while not valid_date:
        try:
            start_input = input("Enter start date (DD/MM/YYYY) >> ")
            end_input = input("Enter end date (DD/MM/YYYY) >> ")

            if start_input == "" or end_input == "":
                return None

            start = datetime.strptime(start_input, "%d/%m/%Y").date()
            end = datetime.strptime(end_input, "%d/%m/%Y").date()

            if (datetime.now().date() - start).days > 0 or (datetime.now().date() - end).days > 0:
                print("Reservation date cannot be before the current date.")
                continue

        except ValueError:
            print("Invalid date. Try again.")
            continue

        days = (end - start).days

        if days < 0:
            print("End date cannot be earlier than the start date.")
            continue

        elif days == 0:
            print("Day difference cannot be 0")
            continue

        else:
            return start, end, start_input, end_input, days


def reserve_attraction(user_id):
    # Handles the complete attraction reservation process.
    # Allows the user to browse, filter and reserve attractions.
    # Saves the reservation and allows the user to proceed to payment.

    clear()
    user_data = load_reserve()
    user_login = load_login()
    current_page = "attractions_search"

    account_login = next(
        data for data in user_login if data["id"] == user_id
    )

    user_filter = account_login["attractions_filter"]

    account = next(
        data for data in user_data if data["id"] == user_id
    )

    city_attractions = apply_filter(
        attraction_data,
        account["city"],
        user_filter
    )

    if account["reservations"].get("attractions") is None:
        account["reservations"]["attractions"] = []

    while current_page != "finished":

        if current_page == "attractions_search":
            print_header("ATTRACTIONS SEARCH")
            print(f"Filter: {user_filter}\n")

            browse_selection = [
                "Browse attractions",
                "Change filters",
                "Reset filters",
                "Back"
            ]

            browse_or_sort = select("", browse_selection)

            if browse_or_sort == "BACK" or browse_or_sort == "Back":
                current_page = "finished"
                return

            elif browse_or_sort == browse_selection[0]:
                current_page = "attractions_selection"

            elif browse_or_sort == browse_selection[1]:
                current_page = "change_filters"

            elif browse_or_sort == browse_selection[2]:
                user_filter = "Default"
                city_attractions = apply_filter(
                    attraction_data,
                    account["city"],
                    user_filter
                )

                account_login["attractions_filter"] = user_filter
                dump_login(user_login)


        if current_page == "change_filters":
            print_header("ATTRACTIONS FILTERS")

            filter_choices = [
                "Default",
                "Category",
                "Price: Low → High",
                "Price: High → Low"
            ]

            new_filter = select(
                "Sort by:",
                filter_choices + ["Back"]
            )

            if new_filter == "BACK" or new_filter == "Back":
                current_page = "attractions_search"
                continue

            elif new_filter == filter_choices[1]:
                clear()
                print_header("SELECT CATEGORY TO FILTER")

                select_category = select(
                    "",
                    attraction_data[
                        attraction_data["City"] == account["city"]
                    ]["Category"].drop_duplicates()
                )

                if select_category == "BACK":
                    current_page = "attractions_search"
                    continue

                new_filter += f": {select_category}"
                user_filter = new_filter

            elif new_filter in filter_choices:
                user_filter = new_filter

            city_attractions = apply_filter(
                attraction_data,
                account["city"],
                user_filter
            )

            current_page = "attractions_search"

            account_login["attractions_filter"] = user_filter
            dump_login(user_login)


        if current_page == "attractions_selection":

            selected_attraction = select_attraction(
                city_attractions,
                account["city"]
            )

            if selected_attraction is None:
                current_page = "attractions_search"

            else:
                clear()

                attraction_name = selected_attraction["Name"]
                attraction_category = selected_attraction["Category"]
                attraction_price = selected_attraction["Entry_Price_MYR"]

                attraction_details = f"""
NAME
{attraction_name}

CATEGORY
{attraction_category}

ENTRY PRICE
RM {attraction_price:.2f} / pax
{'─' * 60}
"""

                print_header("ATTRACTION DETAILS")
                print(attraction_details)

                confirm_reserve = select(
                    "",
                    ["Continue", "Back"]
                )

                if confirm_reserve == "BACK" or confirm_reserve == "Back":
                    current_page = "attractions_selection"

                elif confirm_reserve == "Continue":
                    current_page = "num_ppl"


        if current_page == "num_ppl":
            clear()
            print_header("ENTER NUMBER OF PEOPLE")

            num_ppl = input(
                f"Enter the number of people to reserve for {attraction_name} "
                f"(Maximum reservable per time: 10) >> "
            ).strip()

            if not num_ppl:
                current_page = "attractions_selection"

            elif not num_ppl.isdigit() or int(num_ppl) <= 0:
                print("Number of people must be an integer and not less than or equal to zero.")
                time.sleep(0.5)

            elif int(num_ppl) > 10:
                print("Number of people cannot exceed the maximum reservable capacity.")
                time.sleep(0.5)

            else:
                num_ppl = int(num_ppl)
                current_page = "date"


        if current_page == "date":

            dates = select_attraction_dates()

            if dates is None:
                current_page = "num_ppl"

            else:
                start, end, start_input, end_input, days = dates
                current_page = "continue"


        if current_page == "continue":
            print_header("RESERVATION SUMMARY")

            net_total = attraction_price * num_ppl * days

            final_details = f"""
{attraction_name.upper()}
{'─' * 60}

CATEGORY
{attraction_category}

ENTRY PRICE
RM {attraction_price:.2f} / pax

PERIOD
{start_input} - {end_input}

DAYS
{days} day(s)

PAX
{num_ppl} person(s)

NET TOTAL
RM {net_total:.2f}
{'─' * 60}
"""

            print(final_details)

            confirm = select(
                "Confirm reservation? >> ",
                ["Yes", "No"]
            )

            if confirm == "Yes":

                total_reservations = (
                    sum(len(v) for v in account["reservations"].values()) + 1
                )

                print("\nReserved!\n")

                account["reservations"]["attractions"].append({
                    "reservation_id": total_reservations,
                    "name": attraction_name,
                    "city": account["city"],
                    "category": attraction_category,
                    "start": str(start),
                    "end": str(end),
                    "days": days,
                    "price": float(attraction_price),
                    "pax": num_ppl,
                    "net_total": float(net_total),
                    "paid": False,
                    "expired": False
                })

                dump_reserve(user_data)

                options = [
                    "Proceed to checkout",
                    "Make another reservation",
                    "Quit"
                ]

                print_header("SELECT AN OPTION")
                option = select("", options)

                if option == options[0]:
                    current_page = "finished"
                    return payment(user_id)

                elif option == options[1]:
                    current_page = "finished"
                    return reserve_attraction(user_id)

                elif option == options[2]:
                    current_page = "finished"
                    quit()

            else:
                current_page = "finished"
                return