from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from config import hotel_data
from helpers.cli_helper import clear
import json
from textwrap import dedent
from features.payment import payment
from datetime import datetime, timedelta
import math
import pandas as pd
from helpers.availability_helper import initialize_availability, load_availability, dump_availability

def rating(HotelRating):

    ratings = ["one", "two", "three", "four", "five"]

     # Since "S" in Star from any OneStar, TwoStar, ThreeStar, is at index -4, we can just slice it till the letter before 's' (+1 due to index starting at 0)
    return "★" * (ratings.index(HotelRating.lower()[:-4]) + 1) if HotelRating.lower()[:-4] in ratings else "N/A"

def reserve_hotel(user_id):
    clear()

    current_page = "hotel_selection"
    user_data = load_reserve()
    availability = initialize_availability()

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



    choices = [
        (f"{i+1}. {data["HotelName"]} | {rating(data["HotelRating"])} | RM {data["price"]:.2f}")
        for i, data in specific_hotel_data.iterrows()
    ]  

    while current_page != "finished":

        if current_page == "hotel_selection":
            print(heading)
            hotel = search("", choices, 10)

            if hotel == "BACK":
                current_page = "finished"
                return
            elif hotel is not None:
                choice_index = choices.index(hotel)

                hotel_details = specific_hotel_data.iloc[choice_index]
                hotel_name = hotel_details["HotelName"]
                hotel_rating = rating(hotel_details["HotelRating"])
                hotel_address = hotel_details["Address"]
                hotel_desc = json.loads(hotel_details["Description"])
                hotel_facilities = json.loads(hotel_details["HotelFacilities"])
                hotel_price = hotel_details["price"]
                hotel_fax = hotel_details["FaxNumber"]
                hotel_phone = hotel_details["PhoneNumber"]
                hotel_website = hotel_details["HotelWebsiteUrl"]

                if availability[hotel_name] == 0:
                    clear()
                    print("Oops! It seems that the hotel you were looking for is fully booked. We are sorry for the inconvenience.")
                    input()
                else:
                    current_page = "confirm_reservation"

        if current_page == "confirm_reservation":
            clear()
            details = dedent(f"""
{'─' * 60}
{hotel_name}
{'─' * 60}
{hotel_rating}

📍 {hotel_address}

{hotel_desc[0][:-1]}

Facilities:
{" • ".join(hotel_facilities[:4])}

From RM {hotel_price:.2f} per night

{'─' * 60}
                    """).strip()

            print(details)
            confirm_reserve = select("", ["Continue", "View full details"])

            if confirm_reserve == "BACK":
                current_page = "hotel_selection"

            elif confirm_reserve == "View full details":
                clear()
                full_details = dedent(f"""
{'─' * 60}
HOTEL DETAILS
{'─' * 60}
{hotel_name}
{hotel_rating}

LOCATION
{hotel_address}
                
ABOUT
{"\n".join(hotel_desc[:2])}

FACILITIES
{"• " + "\n• ".join(hotel_facilities[:10])}

CONTACT
Fax: {hotel_fax}
Phone: {hotel_phone}
Website: {hotel_website}

PRICE
Base price: RM {hotel_price:.2f} / night
                """).strip()
                print(full_details)
                input(">> ")
            elif confirm_reserve == "Continue":
                current_page = "continue"

        if current_page == "continue":
            clear()
            room_list = ["Single Room", "Double Room", "Triple Room", "Family Room"]
            room_type = select("Select room type", room_list) #family room means 4 person

            if room_type == "BACK":
                current_page = "confirm_reservation"
            else:

                selected_room_type = room_type.lower().split()[0]
                current_page = "num_rooms"

        if current_page == "num_rooms":
        
            num_rooms = input(f"Enter the number of rooms to reserve for {room_type} (Available rooms: {availability[hotel_name]}) >> ").strip()

            if not num_rooms:
                current_page = "continue"
            elif not num_rooms.isdigit() or not int(num_rooms):
                print("Number of rooms must be an integer and not zero.")
            elif int(num_rooms) > availability[hotel_name]:
                print("Number of rooms cannot exceed the hotel's maximum room capacity.")
            elif num_rooms.isdigit():
                if int(num_rooms) > 7:
                    confirmation = select(f"Are you sure you want to reserve {num_rooms} rooms?", ["Yes", "No"])

                    if confirmation == "No" or confirmation == "BACK":
                        continue


                num_rooms = int(num_rooms)

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
                        current_page = "continue"
                        valid_date = True
                        break
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

    guest_multiplier = 0.364 * math.log(room_list.index(room_type)+1) + 1
    net_total = round(guest_multiplier * hotel_details["price"] * num_rooms * nights ,2) 
    reserve_details = f"""
    Hotel: {hotel_details["HotelName"]}
    Nights : {nights}
    Room type: {selected_room_type}
    Rooms: {num_rooms}
    Price per single room : RM {hotel_details["price"]:.2f}
    Net total: RM {net_total:.2f}
"""

    print(reserve_details)
    account["hotel"].append(
        {
            "name" : hotel_details["HotelName"],
            "rating" : len(rating(hotel_details["HotelRating"])),
            "start" : start_input,
            "end" : end_input,
            "nights" : int(nights),
            "room_type" : selected_room_type,
            "rooms" : int(num_rooms),
            "base_price" : float(hotel_details["price"]),
            "net_total" : float(net_total),
            "paid" : False
        }
    )
    availability[hotel_name] -= num_rooms
    dump_availability(availability)
    dump_reserve(user_data)
    options = ["Proceed to checkout", "Continue with another reservation", "Quit"]
    option = select("Enter option", options)

    if option == options[0]:
        return payment(user_id)
    elif option == options[1]:
        return
    elif option == options[2]:
        quit()