from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from config import car_data
from datetime import datetime
from features.payment import payment
from helpers.cli_helper import clear

def reserve_car(user_id):
    clear()
    current_page = "full_or_segment"
    while current_page != "finished":

        if current_page == "full_or_segment":
            choice = select(f"{"-" * 20}\nCars\n{"-" * 20}", ["Full Criteria Search", "Based on Segment"])

            if choice == "BACK":
                current_page = "finished"
                return

            if choice == "Full Criteria Search":
                # Full criteria includes brand, segment (specific)
                method = "full"
                current_page = "full_brands"

            elif choice == "Based on Segment":
                method = "segment"
                current_page = "segment"

        if current_page == "full_brands":                                            
            brand = search("--- Car Brands ---", car_data["Maker"].drop_duplicates())

            if brand == "BACK":
                current_page = "full_or_segment"
                        
            else : current_page = "full_segment"

        if current_page == "full_segment":
            segment = search(f"--- Segments for {brand} ---", car_data[car_data["Maker"] == brand]["Segment"].drop_duplicates())

            if segment == "BACK":
                current_page = "full_brands"
                        
            else:
                current_page = "full_model"

        if current_page == "full_model":
            car_model = search(f"--- Models for {brand} {segment} ---", car_data[(car_data["Maker"] == brand) & (car_data["Segment"] == segment)]["Genmodel"].drop_duplicates())

            if car_model == "BACK":
                current_page = "full_segment"
                        
            else:
                car_price = float(car_data[(car_data["Maker"] == brand) & (car_data["Segment"] == segment) & (car_data["Genmodel"] == car_model)]["Rental_price"].to_list()[0])
                current_page = "date"

        if current_page == "segment":
                #Includes segments, ignore brand
            segment = search("--- Select Segment ---", car_data["Segment"].drop_duplicates())

            if segment == "BACK":
                current_page = "full_or_segment"
            else:
                current_page = "select_car"

        if current_page == "select_car":

            segment_data = car_data[car_data["Segment"] == segment].drop_duplicates().reset_index(drop=True)

            choices = [
                f"{i+1}. " + " | ".join(str(value) for value in row)
                for i, row in segment_data.iterrows()
            ]
            selected = select("--- Select Car ---", choices)

            if selected == "BACK":
                current_page = "segment"
            else:

                selected_index = choices.index(selected)


                brand = segment_data.iloc[selected_index]["Maker"]
                car_model = segment_data.iloc[selected_index]["Genmodel"]
                car_price = float(segment_data.iloc[selected_index]["Rental_price"]) #per day
                current_page = "date"


        if current_page == "date":
            print(f"{"-" * 20}\nCar Rental Period\n{"-" * 20}")
            valid_date = False
            while not valid_date:
                try:
                    start_input = input("Enter start date (DD/MM/YYYY) >> ")
                    end_input = input("Enter end date (DD/MM/YYYY) >> ")

                    if start_input == "" or end_input == "": #Back
                        
                        if method == "full":
                            current_page = "full_model"
                        elif method == "segment":
                            current_page = "select_car"
                        break
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
                    current_page = "finished"
                    break
            

    car_details = f"""
    {"-" * 20}
    Brand : {brand}
    Model : {car_model}
    Segment : {segment}
    Price : RM {car_price}
    Start date : {start}
    End date: {end}
    Days : {no_of_days}

    {"-" * 20}
    """
    print(car_details)
    confirm = select("Confirm reservation? >> ", ["Yes", "No"])
    if confirm == "Yes":
        print("Reserved!")
        reserve_data = load_reserve()

        for data in reserve_data:
            if data["id"] == user_id:
                if data.get("car") is None:
                    data["car"] = []
                        
                data["car"].append({
                    "brand" : brand,
                    "model" : car_model,
                    "segment" : segment,
                    "price" : car_price,
                    "start_date" : str(start),
                    "end_date" : str(end),
                    "days" : no_of_days
                })

        dump_reserve(reserve_data)
        options = ["Proceed to checkout", "Continue with another reservation", "Quit"]
        option = select("Enter option", options)

        if option == options[0]:
            return payment(user_id)
        elif option == options[1]:
            return
        elif option == option[2]:
            quit()