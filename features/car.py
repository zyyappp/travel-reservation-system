from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from config import car_data
from datetime import datetime
from features.payment import payment
from helpers.cli_helper import clear, print_header


def select_car_by_segment(segment):

    print_header(f"CAR RESERVATION - {segment.upper()}")

    segment_data = car_data[
        car_data["Segment"] == segment
    ].drop_duplicates().reset_index(drop=True)

    choices = [
        f"{f'{i+1}.':<5} {row['Maker']:<15} | {row['Genmodel']:<25} | RM {float(row['Rental_price']):.2f}"
        for i, row in segment_data.iterrows()
    ]

    selected = select("", choices)

    if selected == "BACK":
        return None

    selected_index = choices.index(selected)

    brand = segment_data.iloc[selected_index]["Maker"]
    car_model = segment_data.iloc[selected_index]["Genmodel"]
    car_price = float(segment_data.iloc[selected_index]["Rental_price"])

    return brand, car_model, car_price


def select_car_dates():

    print_header("CAR RENTAL PERIOD")

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

        no_of_days = (end - start).days

        if no_of_days < 0:
            print("End date cannot be earlier than the start date.")
            continue

        elif no_of_days == 0:
            print("Day difference cannot be 0")
            continue

        else:
            valid_date = True
            return start, end, start_input, end_input, no_of_days


def reserve_car(user_id):

    clear()

    current_page = "full_or_segment"

    while current_page != "finished":

        if current_page == "full_or_segment":

            clear()
            print_header("CAR RESERVATION")

            choice = select(
                "",
                ["Full Criteria Search", "Based on Segment", "Back"]
            )

            if choice == "BACK" or choice == "Back":
                current_page = "finished"
                return

            if choice == "Full Criteria Search":
                method = "full"
                current_page = "full_brands"

            elif choice == "Based on Segment":
                method = "segment"
                current_page = "segment"


        if current_page == "full_brands":

            print_header("CAR RESERVATION - SELECT BRAND")

            brand = search(
                "",
                car_data["Maker"].drop_duplicates()
            )

            if brand == "BACK":
                current_page = "full_or_segment"

            elif brand is not None:
                current_page = "full_segment"


        if current_page == "full_segment":

            clear()
            print_header("CAR RESERVATION - SELECT SEGMENT")

            segment = search(
                "",
                car_data[
                    car_data["Maker"] == brand
                ]["Segment"].drop_duplicates()
            )

            if segment == "BACK":
                current_page = "full_brands"

            elif segment is not None:
                current_page = "full_model"


        if current_page == "full_model":

            clear()
            print_header("CAR RESERVATION - SELECT MODEL")

            car_model = search(
                "",
                car_data[
                    (car_data["Maker"] == brand) &
                    (car_data["Segment"] == segment)
                ]["Genmodel"].drop_duplicates()
            )

            if car_model == "BACK":
                current_page = "full_segment"

            elif car_model is not None:

                car_price = float(
                    car_data[
                        (car_data["Maker"] == brand) &
                        (car_data["Segment"] == segment) &
                        (car_data["Genmodel"] == car_model)
                    ]["Rental_price"].to_list()[0]
                )

                current_page = "date"


        if current_page == "segment":

            print_header("CAR RESERVATION - SELECT SEGMENT")

            segment = search(
                "",
                car_data["Segment"].drop_duplicates()
            )

            if segment == "BACK":
                current_page = "full_or_segment"

            elif segment is not None:
                current_page = "select_car"


        if current_page == "select_car":

            selected_car = select_car_by_segment(segment)

            if selected_car is None:
                current_page = "segment"

            else:
                brand, car_model, car_price = selected_car
                current_page = "date"


        if current_page == "date":

            dates = select_car_dates()

            if dates is None:

                if method == "full":
                    current_page = "full_model"

                elif method == "segment":
                    current_page = "select_car"

                continue

            start, end, start_input, end_input, no_of_days = dates
            current_page = "reserved"


        if current_page == "reserved":

            net_total = car_price * no_of_days

            car_details = f"""
BRAND
{brand}

MODEL
{car_model}

SEGMENT
{segment}

PERIOD
{start_input} - {end_input}

BASE PRICE 
RM {car_price:.2f} / day

NET TOTAL
RM {net_total:.2f}
"""

            print_header("RESERVATION SUMMARY")
            print(car_details)

            confirm = select(
                "Confirm reservation? >> ",
                ["Yes", "No"]
            )

            if confirm == "Yes":

                print("\nReserved!\n")

                user_data = load_reserve()

                account = next(
                    data for data in user_data
                    if data["id"] == user_id
                )

                if account.get("car") is None:
                    account["reservations"]["car"] = []

                total_reservations = (
                    sum(len(v) for v in account["reservations"].values()) + 1
                )

                account["reservations"]["car"].append(
                    {
                        "reservation_id": total_reservations,
                        "name": f"{brand} {car_model}",
                        "city": account["city"],
                        "brand": brand,
                        "model": car_model,
                        "segment": segment,
                        "price": car_price,
                        "net_total": net_total,
                        "start": str(start),
                        "end": str(end),
                        "days": no_of_days,
                        "paid": False,
                        "expired": False
                    }
                )

                dump_reserve(user_data)

                options = [
                    "Proceed to checkout",
                    "Make another reservation",
                    "Quit"
                ]

                option = select("", options)

                current_page = "finished"

                if option == options[0]:
                    return payment(user_id)

                elif option == options[1]:
                    current_page = "full_or_segment"

                elif option == options[2]:
                    quit()