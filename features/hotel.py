from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from config import hotel_data
from helpers.cli_helper import clear, print_header
import json
from textwrap import dedent
from features.payment import payment
from datetime import datetime
import math
from helpers.availability_helper import initialize_availability, dump_availability
from helpers.login_helper import load_login, dump_login

#backlog: make reserve_hotel() more clean by splitting the function into more smaller functions

def rating(HotelRating):

    ratings = ["one", "two", "three", "four", "five"]

     # Since "S" in Star from any OneStar, TwoStar, ThreeStar, is at index -4, we can just slice it till the letter before 's' (+1 due to index starting at 0)
    return "★" * (ratings.index(HotelRating.lower()[:-4]) + 1) if HotelRating.lower()[:-4] in ratings else "N/A"

def apply_filter(data, city, user_filter): #takes attraction data
    city_hotels = data[data["cityName"] == city]

    if user_filter == "Default":
        pass

    elif user_filter == "Price: Low → High":
        city_hotels = city_hotels.sort_values("price")
    elif user_filter == "Price: High → Low":
        city_hotels = city_hotels.sort_values("price", ascending=False)
    elif user_filter == "Rating: Low → High":
        city_hotels = city_hotels.sort_values(
                            by = "HotelRating",
                            key = lambda series: series.map(lambda r : len(rating(r)) if rating(r) != "N/A" else 0), # series = whole HotelRating series -> (each value mapped to r) -> passed to function
                        )
    elif user_filter == "Rating: High → Low":
        city_hotels = city_hotels.sort_values(
                            by = "HotelRating",
                            key = lambda series: series.map(lambda r : len(rating(r)) if rating(r) != "N/A" else 0) ,
                            ascending = False
                        )
    elif user_filter == "Name: A → Z":
        city_hotels = city_hotels.sort_values("HotelName")

    return city_hotels.reset_index(drop=True)


def reserve_hotel(user_id):
    #filtering
    clear()

    current_page = "hotel_search"
    user_data = load_reserve()
    user_login = load_login()
    availability = initialize_availability()

    account_login = next(
            data for data in user_login if data["id"] == user_id
        )
    account = next(
        data for data in user_data if data["id"] == user_id
    )

    if account["reservations"].get("hotel") is None:
        account["reservations"]["hotel"] = []

    user_filter = account_login["hotel_filter"]
    city_hotels = apply_filter(hotel_data, account["city"], user_filter)
    while current_page != "finished":

        if current_page == "hotel_search":
            clear()
            search_heading = f"""
{'─' * 60}
HOTEL SEARCH
{'─' * 60}

Filter: {user_filter}
"""     
            print(search_heading)
            browse_selection = ["Browse hotels", "Change filters", "Reset filters", "Back"]
            browse_or_sort = select("", browse_selection)

            if browse_or_sort == "BACK" or browse_or_sort == "Back":
                current_page = "finished"
                return
            elif browse_or_sort == browse_selection[0]:
                current_page = "hotel_selection"
            elif browse_or_sort == browse_selection[1]:
                current_page = "change_filters"
            elif browse_or_sort == browse_selection[2]:
                city_hotels = hotel_data[hotel_data["cityName"] == account["city"]].reset_index(drop=True)
                user_filter = "Default"

        if current_page == "change_filters":
            clear()
            print_header("SELECT FILTER")

            filter_choices = ["Default", "Price: Low → High", "Price: High → Low", "Rating: Low → High", "Rating: High → Low", "Name: A → Z", "Back"]
            new_filter = select("Sort by:", filter_choices)

            if new_filter == "BACK" or new_filter == "Back":
                current_page = "hotel_search"

                continue
            else:
                user_filter = new_filter


            city_hotels = apply_filter(hotel_data, account["city"], user_filter)
            account_login["hotel_filter"] = user_filter
            dump_login(user_login)
            current_page = "hotel_search"

            
        if current_page == "hotel_selection":
            choices = [
        (f"{f'{i+1}.':<5} {data["HotelName"]:<115} | {rating(data["HotelRating"]):<5} | RM {data["price"]:.2f}")
        for i, data in city_hotels.iterrows()
                        ]  
            clear()
            print_header(f"HOTELS IN {account["city"].upper()}")

            hotel = search("", choices, 10)

            if hotel == "BACK":
                current_page = "hotel_search"

            elif hotel is not None:
                choice_index = choices.index(hotel)

                hotel_details = city_hotels.iloc[choice_index]
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
{" • ".join(facility.capitalize() for facility in hotel_facilities[:4]) or "NONE"}

From RM {hotel_price:.2f} per night

{'─' * 60}
""").strip()

            print(details)
            confirm_reserve = select("", ["Continue", "View full details", "Back"])

            if confirm_reserve == "BACK" or confirm_reserve == "Back":
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
{"• " + "\n• ".join(facility.capitalize() for facility in hotel_facilities[:10])}

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
            room_list = ["Single Room", "Double Room", "Triple Room", "Family Room"]
            print_header("SELECT ROOM TYPE")
            room_type = select("", room_list + ["Back"]) #family room means 4 person

            if room_type == "BACK":
                current_page = "confirm_reservation"
                continue
            else:

                selected_room_type = room_type.lower().split()[0]
                current_page = "num_rooms"

        if current_page == "num_rooms":
        
            num_rooms = input(f"Enter the number of rooms to reserve for {room_type} (Available rooms: {availability[hotel_name]}) >> ").strip()

            if not num_rooms:
                current_page = "continue"
            elif not num_rooms.isdigit() or int(num_rooms) <=0:
                print("Number of rooms must be an integer and not less than or equal to zero.")
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
            clear()
            valid_date = False
            print_header("HOTEL RESERVATION PERIOD")
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
                    current_page = "reserved"
        if current_page == "reserved":
            guest_multiplier = 0.364 * math.log(room_list.index(room_type)+1) + 1
            net_total = round(guest_multiplier * hotel_details["price"] * num_rooms * nights ,2) 

            reserve_details = f"""
NAME
{hotel_name}

PERIOD
{start_input} - {end_input}

NIGHTS
{nights} night(s)

ROOM TYPE
{selected_room_type.upper()}

NO. OF ROOMS
{num_rooms} room(s)

BASE PRICE (SINGLE)
RM {hotel_price:.2f} / night

NET TOTAL
RM {net_total:.2f}
"""
            clear()
            print_header("RESERVATION SUMMARY")
            print(reserve_details)
            confirm = select("Confirm reservation? >> ", ["Yes", "No"])
            if confirm == "Yes":
                print("\nReserved!\n")
                total_reservations = sum(len(v) for v in account["reservations"].values()) + 1
                account["reservations"]["hotel"].append(
            {
                "reservation_id" : total_reservations,
                "name" : hotel_details["HotelName"],
                "rating" : len(rating(hotel_details["HotelRating"])),
                "start" : str(start),
                "end" : str(end),
                "nights" : int(nights),
                "room_type" : selected_room_type,
                "rooms" : int(num_rooms),
                "base_price" : float(hotel_details["price"]),
                "net_total" : float(net_total),
                "paid" : False,
                "expired" : False
            }
        )
                availability[hotel_name] -= num_rooms
                dump_availability(availability)
                dump_reserve(user_data)
                options = ["Proceed to checkout", "Continue with another reservation", "Quit"]
                option = select("", options)
                current_page = "finished"
                if option == options[0]:
                    return payment(user_id)
                elif option == options[1]:
                    current_page = "hotel_search"
                elif option == "BACK":
                    return 
                elif option == options[2]:
                    quit()