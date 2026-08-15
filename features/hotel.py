from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from config import hotel_data
from helpers.cli_helper import clear

def stars():
    pass

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

    hotel = search("", choices, 10)
    