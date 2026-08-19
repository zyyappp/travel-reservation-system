from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from helpers.cli_helper import clear
from config import attraction_data

def reserve_attraction(user_id):
    clear()
    user_data = load_reserve()
    current_page = "attractions_search"
    user_filter = "Default"

    account = next(data for data in user_data if data["id"] == user_id)
    city_attractions = attraction_data[attraction_data["City"] == account["city"]].reset_index(drop=True)
    
    if account.get("attractions") is None:
        account["attractions"] = []


    while current_page != "finished":

        if current_page == "attractions_search":
            clear()
            search_heading = f"""
{'─' * 60}
ATTRACTIONS SEARCH
{'─' * 60}

Filter: {user_filter}
            """     
            print(search_heading)
            browse_selection = ["Browse attractions", "Change filters", "Reset filters"]
            browse_or_sort = select("", browse_selection)

            if browse_or_sort == "BACK":
                current_page = "finished"
                return
            elif browse_or_sort == browse_selection[0]:
                current_page = "attractions_selection"
            elif browse_or_sort == browse_selection[1]:
                current_page = "change_filters"
            elif browse_or_sort == browse_selection[2]:
                
                user_filter = "Default"

        if current_page == "attractions_selection":
            choices = [
                    (f"{i+1}. {data["Name"]} | {data["Category"]} | RM {data["Entry_Price_MYR"]:.2f}")
                    for i, data in city_attractions.iterrows()
                                    ]  
            attraction_heading = f"""
{'─' * 60}
ATTRACTIONS IN {account["city"].upper()}
{'─' * 60}
"""  
            print(attraction_heading)
            user_attraction = search("", choices, 10)

            if user_attraction == "BACK":
                current_page = "attractions_search"
            elif user_attraction is not None:
                #reservation
                choice_index = choices.index(user_attraction)
                attraction_details = city_attractions.iloc[choice_index]
                print(attraction_details)
                pass