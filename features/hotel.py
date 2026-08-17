from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from config import hotel_data
from helpers.cli_helper import clear
import json
import time
from features.payment import payment
from datetime import datetime, timedelta

def rating(HotelRating):

    ratings = ["one", "two", "three", "four", "five"]

    stars = (ratings.index(HotelRating.lower()[:-4]) + 1) # Since "S" in Star from any OneStar, TwoStar, ThreeStar, is at index -4, we can just slice it till the letter before 's' (+1 due to index starting at 0)
    return "⋆" * stars

def reserve_hotel(user_id):
    clear()

    current_page = "hotel_selection"
    user_data = load_reserve()

    account = next(
        data for data in user_data if data["id"] == user_id
    )

    specific_hotel_data = hotel_data[hotel_data["cityName"] == account["city"]].reset_index(drop=True)

    if account.get("hotel") is None:
        account["hotel"] = []


    heading = f"""
    {'─' * 60}
                           HOTELS IN {account["city"]}
    {'─' * 60}
    """

    print(heading)

    choices = [
        (f"{i+1}. {data["HotelName"]} | RM {data["price"]:.2f}")
        for i, data in specific_hotel_data.iterrows()
    ]  

    while current_page != "finished":

        if current_page == "hotel_selection":
            hotel = search("", choices, 10)

            if hotel == "BACK":
                current_page = "finished"
            else:

                choice_index = choices.index(hotel)

                hotel_details = specific_hotel_data.iloc[choice_index]

                details = f"""
                {'─' * 60}
                Hotel: {hotel_details["HotelName"]}
                Rating: {rating(hotel_details["HotelRating"])}
                Location: {hotel_details["Address"]}
                Description : {json.loads(hotel_details["Description"])[0][:-1]}
                Facilities: {json.loads(hotel_details["HotelFacilities"])[:4]}
                Fax: {hotel_details["FaxNumber"]}
                Website: {hotel_details["HotelWebsiteUrl"]}

                {'─' * 60}
                """

                print(details)
                current_page = "confirm_reservation"

        if current_page == "confirm_reservation":
            confirm_reserve = select("Confirm reservation or learn more", ["View full details", "Confirm Reservation"])

            if confirm_reserve == "BACK":
                current_page = "hotel_selection"

            elif confirm_reserve == "View full details":
                print("----")
                #insert full details code
            elif confirm_reserve == "Confirm Reservation":
                current_page = "confirm"

        if current_page == "confirm":
            clear()
            no_of_rooms = input("How many rooms to book?\nYou are only able to book at most 10 rooms at once.\n >> ")

            if not no_of_rooms:
                current_page = "finished"
                return

            elif not no_of_rooms.isdigit():
                print("Must be an integer.")
                time.sleep(0.5)
                continue
            elif int(no_of_rooms) > 10:
                print("Number of rooms exceeded maximum limit.")
                time.sleep(0.5)
                continue
            else:
                no_of_rooms = int(no_of_rooms)
                current_page = "date"


        if current_page == "date":
            valid_date = False
            print(f"""
            {'─' * 60}
                                HOTEL RESERVATION PERIOD
            {'─' * 60}
            """)
            while not valid_date:
                try:
                    start_input = input("Enter start date (DD/MM/YYYY) >> ")
                    end_input = input("Enter end date (DD/MM/YYYY) >> ")

                    if start_input == "" or end_input == "": #Back
                        current_page = "confirm"
                        valid_date = True
                        continue
                    start = datetime.strptime(start_input, "%d/%m/%Y").date()
                    end = datetime.strptime(end_input, "%d/%m/%Y").date()

                    if (datetime.now().date() - start).days > 0 or (datetime.now().date() - end).days > 0:
                        print("Reservation date cannot be before the current date.")
                        continue    
                except ValueError:
                    print("Invalid date. Try again.")
                    continue

                nights = (end - start).days 

                if nights < 0:
                    print("End date cannot be earlier than the start date.")
                    continue
                elif nights == 0:
                    print("Night difference cannot be 0")
                    continue
                else:
                    valid_date = True
                    current_page = "finished"
    net_total = no_of_rooms * hotel_details["price"]
    reserve_details = f"""
    Hotel: {hotel_details["HotelName"]}
    Nights : {nights}
    Rooms : {no_of_rooms}
    Price per room : {hotel_details["price"]}
    Net total: RM {net_total}
"""

    print(reserve_details)
    account["hotel"].append(
        {
            "name" : hotel_details["HotelName"],
            "nights" : int(nights),
            "rooms" : int(no_of_rooms),
            "price_per_room" : float(hotel_details["price"]),
            "net_total" : float(net_total)
        }
    )
    dump_reserve(user_data)
    options = ["Proceed to checkout", "Continue with another reservation", "Quit"]
    option = select("Enter option", options)

    if option == options[0]:
        return payment(user_id)
    elif option == options[1]:
        return
    elif option == option[2]:
        quit()