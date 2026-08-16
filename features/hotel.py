from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from config import hotel_data
from helpers.cli_helper import clear
import json

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
            elif confirm_reserve == "Confirm Reservation":
                current_page = "confirm"

        if current_page == "confirm":
            no_of_rooms = input("How many rooms to book?\nYou are only able to book at most 10 rooms at once.\n >> ")

            if not no_of_rooms:
                current_page = "finished"

            elif not no_of_rooms.isdigit():
                print("Must be an integer.")
                continue
            else:
                pass #booking

    