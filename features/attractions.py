from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from helpers.cli_helper import clear
from config import attraction_data
from datetime import datetime
from features.payment import payment
import time

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

        if current_page == "change_filters":
            filter_choices = ["Default", "Category", "Price: Low → High", "Price: High → Low"]
            user_filter = select("Sort by:", filter_choices)

            if user_filter == "BACK":
                current_page = "attraction_search"
                continue

            current_page = "attraction_search"

        if current_page == "attractions_selection":
            if city_attractions.empty:
                clear()
                print("Oops! It seems that there are no attraction places in this city. Please try another city.")
                input()
                current_page = "finished"
                return
            else:

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
                    clear()
                    #reservation
                    choice_index = choices.index(user_attraction)
                    selected_attraction = city_attractions.iloc[choice_index]
                    attraction_name = selected_attraction["Name"]
                    attraction_category = selected_attraction["Category"]
                    attraction_price = selected_attraction["Entry_Price_MYR"]

                    

                    attraction_details = f"""
{'─' * 60}
{attraction_name.upper()}
{'─' * 60}

CATEGORY
{attraction_category}

ENTRY PRICE
RM {attraction_price:.2f} / pax
{'─' * 60}
                                          """

                    print(attraction_details)
                    confirm_reserve = select("", ["Continue", "Back"])

                    if confirm_reserve == "BACK" or confirm_reserve == "Back":
                        current_page = "attractions_selection"

                    elif confirm_reserve == "Continue":
                        current_page = "num_ppl"

        if current_page == "num_ppl":
            clear()
            num_ppl = input(f"Enter the number of people to reserve for {attraction_name} (Maximum reservable per time: 10) >> ").strip()

            if not num_ppl:
                current_page = "attractions_selection"
            elif not num_ppl.isdigit() or int(num_ppl) <=0:
                print("Number of people must be an integer and not less than or equal to zero.")
                time.sleep(0.5)
            elif int(num_ppl) > 10:
                print("Number of rooms cannot exceed the hotel's maximum room capacity.")
                time.sleep(0.5)
            elif num_ppl.isdigit():

                num_ppl = int(num_ppl)

                current_page = "date"
        if current_page == "date":
            clear()
            valid_date = False
            print(f"""
            {'─' * 60}
                                ATTRACTION RESERVATION PERIOD
            {'─' * 60}
            """)
            while not valid_date:
                try:
                    start_input = input("Enter start date (DD/MM/YYYY) >> ")
                    end_input = input("Enter end date (DD/MM/YYYY) >> ")

                    if start_input == "" or end_input == "": #Back
                        current_page = "num_ppl"
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

                days = (end - start).days 

                if days < 0:
                    print("End date cannot be earlier than the start date.")
                    continue
                elif days == 0:
                    print("Day difference cannot be 0")
                    continue
                else:
                    valid_date = True
                    current_page = "continue"
        if current_page == "continue":
            clear()
            net_price = attraction_price * num_ppl * days
            account["attractions"].append({
                "name" : attraction_name,
                "category" : attraction_category,
                "start" : start_input,
                "end" : end_input,
                "days" : days,
                "price" : float(attraction_price),
                "pax" : num_ppl,
                "net_price" : float(net_price)
            })
            dump_reserve(user_data)

            final_details = f"""
{'─' * 60}
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
RM {net_price:.2f}
{'─' * 60}
                                                      """
            print(final_details)
            options = ["Proceed to checkout", "Continue with another reservation", "Quit"]
            option = select("Enter option", options)
            if option == options[0]:
                return payment(user_id)
            elif option == options[1] or option == "BACK":
                return
            elif option == options[2]:
                quit()