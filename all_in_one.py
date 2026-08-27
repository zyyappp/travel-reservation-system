# Consolidated standalone version of the travel reservation system.


# Generated from the project's Python modules; run with: python all_in_one.py


from pathlib import Path
from datetime import datetime, timedelta
from textwrap import dedent
import json
import math
import os
import platform
import re
import subprocess
import time

import pandas as pd
from InquirerPy import inquirer


# ============================================================================
# Source: config.py
# ============================================================================
#module name  : config.py
#date created : 11th August 2026
#created by   : 
#imported     : pathlib, pandas, os
#amendment    :
#remark       : Configuration


BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)
(BASE_DIR / "saves").mkdir(parents=True, exist_ok=True)

LOGIN_PATH = BASE_DIR / "saves" / "login.json"
RESERVES_PATH = BASE_DIR / "saves" / "reserves.json"
ROOM_AVAILABILITY_PATH = BASE_DIR / "saves" / "room_availability.json"
TRANSACTION_PATH = BASE_DIR / "saves" / "transaction_history.json"
DATA_FOLDER = BASE_DIR / "data"

hotel_data = pd.read_csv(DATA_FOLDER / "malaysia_hotels.csv")
car_data = pd.read_csv(DATA_FOLDER /"car_models.csv")
attraction_data = pd.read_csv(DATA_FOLDER / "malaysia_attractions.csv")

# pd.read_csv reads the .csv file and outputs a DataFrame


# ============================================================================
# Source: features/__init__.py
# ============================================================================
#module name  : __init__.py
#date created : 13th August 2026
#created by   : Yap Zi Yi
#imported     : config, json
#amendment    :
#remark       : Declare folder as module & loading & dumping jsons


def dump_reserve(info):
    with open(RESERVES_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)

def load_reserve():
    try:
        with open(RESERVES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        dump_reserve([])
        return []


# ============================================================================
# Source: helpers/selection_helper.py
# ============================================================================
#module name  : selection_helper.py
#date created : 13th August 2026
#created by   : 
#imported     : InquirerPy
#amendment    :
#remark       : Selection, Searching, Checkbox UI



def select(message, choices, height = 10): 

    prompt = inquirer.select(
            message=message,
            choices=choices,
            max_height=height,
        )

    @prompt.register_kb("escape")
    def _(event):
        event.app.exit(result="BACK")

    return prompt.execute()

    

def search(message, choices, height = 10): 

    prompt = inquirer.fuzzy(
            message=message,
            choices=choices,
            max_height=height,
        )

    @prompt.register_kb("escape")
    def _(event):
        event.app.exit(result="BACK")

    return prompt.execute()

def checkbox(message, choices, height=10):

    prompt = inquirer.checkbox(
            message=message,
            choices=choices,
            max_height=height,
        )

    @prompt.register_kb("escape")
    def _(event):
        event.app.exit(result="BACK")

    return prompt.execute()


# ============================================================================
# Source: helpers/cli_helper.py
# ============================================================================
#module name  : cli_helper.py
#date created : 13th August 2026
#created by   :
#imported     : subprocess, platform
#amendment    :
#remark       : clearing CLI & printing UI

def clear():
    if platform.system() == "Windows":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)

def print_header(title, quantity=60):
        clear()
        print(f"\n{'─'*quantity}\n{title}\n{'─'*quantity}\n")


# ============================================================================
# Source: helpers/expiry_helper.py
# ============================================================================
#module name  : expiry_helper.py
#date created : 25th August 2026
#created by   : 
#imported     : datetime
#amendment    :
#remark       : Check whether a reservation expired


def check_expired_reservations(account):
    today = datetime.now().date()

    for reservations in account["reservations"].values():
        for reservation in reservations:

            if reservation["paid"]:
                continue

            start_date = datetime.strptime(
                reservation["start"],
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                reservation["end"],
                "%Y-%m-%d"
            ).date()

            if today > start_date or today > end_date:
                reservation["expired"] = True

    return account


# ============================================================================
# Source: helpers/availability_helper.py
# ============================================================================
#module name  : availability_helper.py
#date created : 19th August 2026
#created by   : 
#imported     : config, json
#amendment    :
#remark       : Loading and dumping room_availability.json


def dump_availability(info):
    with open(ROOM_AVAILABILITY_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)

def load_availability():
    try:
        with open(ROOM_AVAILABILITY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        dump_availability({})
        return {}

def initialize_availability():
    available = load_availability()

    if not available:
        available = {hotel["HotelName"] : int(hotel["max_rooms"]) for _, hotel in hotel_data.iterrows()}
        dump_availability(available)

    return available


# ============================================================================
# Source: features/city.py
# ============================================================================
#module name  : city.py
#date created : 13th August 2026
#created by   : 
#imported     : features, helpers.selection_helper, config, helpers.cli_helper
#amendment    :
#remark       : City selection


def select_city(user_id):
    current_page = "city_selection"
    reserve_data = load_reserve()
    for data in reserve_data:
        if data["id"] == user_id:
            return data["city"]

    while current_page != "finished":
        print_header("SELECT CITY")
        city = search("", hotel_data["cityName"].drop_duplicates())

        if city == "BACK":
            continue
        elif city is None:
            print("City not found. Try again")
            continue
        else:
            reserve_data.append(
                {
                        "id" : user_id,
                        "city" : city,
                        "reservations" : {}
                }
            )
            dump_reserve(reserve_data)
            current_page = "finished"
            return city

def switch_city(user_id):
    current_page = "switch_city"
    reserve_data = load_reserve()
    for data in reserve_data:
        if data["id"] == user_id:

            while current_page != "finished":
                print_header("SWITCH CITY")
                city = search("", hotel_data["cityName"].drop_duplicates())

                if city == "BACK":
                    current_page = "finished"
                    return data["city"]
                elif city is None:
                    print("City not found. Try again")
                    continue
                else:
                    data["city"] = city

                    dump_reserve(reserve_data)
                    current_page = "finished"
                    return city


# ============================================================================
# Source: user_class.py
# ============================================================================
#module name  : login_helper.py
#date created : 13th August 2026
#created by   : 
#imported     : features.city
#amendment    :
#remark       : User class

class User:
    def __init__(self, id, user, password, hotel, attractions, reservations):
        self.id = id
        self.user = user
        self.password = password
        self.city = select_city(id)
        self.hotel_filter = hotel
        self.attractions_filter = attractions
        self.reservations_filter = reservations


# ============================================================================
# Source: helpers/login_helper.py
# ============================================================================
#module name  : login_helper.py
#date created : 11th August 2026
#created by   : Yap Zi Yi
#imported     : json, re (regex), datetime, config, user_class, helpers.selection_helper, helpers.selection_helper, features, helpers.expiry_helper
#amendment    :
#remark       : Login


def dump_login(info):
    # Takes the login data and saves it into the login JSON file.

    with open(LOGIN_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)


def load_login():
    # Loads and returns the login data from the login JSON file.
    # Creates an empty login file if the file does not exist or is invalid.

    try:
        with open(LOGIN_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.decoder.JSONDecodeError, FileNotFoundError):
        dump_login([])
        return []


def update_expiry(user_id):
    # Takes the user's ID and checks the user's reservations for expiry.
    # Saves any updated reservation expiry status into the reservation file.

    reservation_data = load_reserve()

    account = next(
        (data for data in reservation_data if data["id"] == user_id),
        None
    )

    if account is None:
        return

    check_expired_reservations(account)

    dump_reserve(reservation_data)


def get_username(previous_page=None, user_id=None):
    # Gets and validates a username entered by the user.
    # Returns a valid username or returns to the previous page when available.

    while True:

        username = input("Enter username >> ")

        if username == "":

            if previous_page is None:
                continue

            else:
                clear()
                return previous_page(user_id)

        elif len(username) < 3:
            print("Username must be greater than 2 in length")
            continue

        elif re.search(r"\s", username):
            print("Username must not include spaces")
            continue

        if username in [data["user"] for data in load_login()]:
            print("Username already exists")
            continue

        return username


def get_password(previous_page=None, user_id=None):
    # Gets and validates a password entered by the user.
    # Ensures the password meets the required password conditions.

    while True:

        password = input("Enter password >> ")

        if password == "":

            if previous_page is None:
                continue

            else:
                return previous_page(user_id)

        if len(password) <= 3:
            print("Password must be greater than 3 in length")
            continue

        if not re.search(r"[^A-Za-z0-9\s]", password):
            print("Password must include at least 1 special character")
            continue

        if not re.search(r"[A-Z]", password):
            print("Password must include at least 1 uppercase character")
            continue

        if not re.search(r"[a-z]", password):
            print("Password must include at least 1 lowercase character")
            continue

        if re.search(r"\s", password):
            print("Password must not include spaces")
            continue

        if not re.search(r"[0-9]", password):
            print("Password must include at least 1 digit")
            continue

        return password


def get_recent_login(login_data):
    # Checks if an account has logged in within the last 15 minutes.
    # Returns the index of the most recently used account or None.

    earliest_login = None

    for i, login in enumerate(login_data):

        now = datetime.now()

        login_time = datetime.strptime(
            login["last_login"],
            "%Y-%m-%d %H:%M:%S.%f"
        )

        time_diff = now - login_time

        if time_diff <= timedelta(minutes=15):

            if earliest_login is None:
                earliest_login = i

            elif (
                time_diff <
                (
                    now -
                    datetime.strptime(
                        login_data[earliest_login]["last_login"],
                        "%Y-%m-%d %H:%M:%S.%f"
                    )
                )
            ):
                earliest_login = i

    return earliest_login


def register_user(user_id=None, previous_page=None):
    # Handles the creation of a new user account.
    # Validates the username and password before saving the account.
    # Returns a User object for the newly registered account.

    clear()
    print_header("CREATE ACCOUNT")

    login_data = load_login()

    username = get_username(previous_page, user_id)

    if not isinstance(username, str):
        return username

    password = get_password(previous_page, user_id)

    if not isinstance(password, str):
        return password

    data = {
        "id": len(login_data) + 1,
        "user": username,
        "password": password,
        "date_created": str(datetime.now()),
        "last_login": str(datetime.now()),
        "hotel_filter": "Default",
        "attractions_filter": "Default",
        "reservations_filter": "Default"
    }

    login_data.append(data)

    dump_login(login_data)

    return User(
        data["id"],
        username,
        password,
        data["hotel_filter"],
        data["attractions_filter"],
        data["reservations_filter"]
    )


def login_user(user_id=None):
    # Handles user login and registration.
    # Automatically logs into a recently used account within 15 minutes.
    # Updates reservation expiry and returns the logged-in User object.

    login_data = load_login()

    if not login_data:
        print_header("REGISTER ACCOUNT")
        return register_user()

    earliest_login = get_recent_login(login_data)

    if earliest_login is None:

        clear()
        current_page = "reg_or_login"

        while current_page != "finished":

            if current_page == "reg_or_login":

                clear()
                print_header("REGISTER OR LOGIN")

                reg_or_login = select(
                    "",
                    [
                        "Login to existing account",
                        "Register a new account"
                    ]
                )

                if reg_or_login == "BACK":
                    current_page = "reg_or_login"

                if reg_or_login == "Register a new account":
                    current_page = "finished"
                    return register_user(previous_page=login_user)

                if reg_or_login == "Login to existing account":
                    current_page = "login"


            if current_page == "login":

                print_header("LOGIN ACCOUNT")

                username = input("Enter username >> ")
                password = input("Enter password >> ")

                if not username:
                    current_page = "reg_or_login"
                    continue

                for log in login_data:

                    if log["user"] == username and log["password"] == password:

                        current_page = "finished"

                        log["last_login"] = str(datetime.now())

                        dump_login(login_data)

                        update_expiry(log["id"])

                        return User(
                            log["id"],
                            username,
                            password,
                            log["hotel_filter"],
                            log["attractions_filter"],
                            log["reservations_filter"]
                        )

                print("Invalid username or password.")

                time.sleep(0.5)
                clear()


    else:

        latest_login = login_data[earliest_login]

        latest_login["last_login"] = str(datetime.now())

        dump_login(login_data)

        update_expiry(latest_login["id"])

        return User(
            latest_login["id"],
            latest_login["user"],
            latest_login["password"],
            latest_login["hotel_filter"],
            latest_login["attractions_filter"],
            latest_login["reservations_filter"]
        )


def manage_accounts(user_id):
    # Handles account management for the current user.
    # Allows the user to switch accounts, add accounts or delete an account.
    # Returns the User object for the account that remains logged in.

    current_page = "login_selection"
    login_data = load_login()

    account = next(
        data for data in login_data if data["id"] == user_id
    )

    while current_page != "finished":

        print_header(
            f"MANAGE ACCOUNT - {account['user'].upper()}"
        )

        login_type = [
            "Login to existing account",
            "Add a new account",
            "Delete account",
            "Back"
        ]

        selection = select("", login_type)

        if selection == "BACK" or selection == "Back":

            current_page = "finished"

            return User(
                user_id,
                account["user"],
                account["password"],
                account["hotel_filter"],
                account["attractions_filter"],
                account["reservations_filter"]
            )


        if selection == login_type[0]:
            current_page = "login_existing"


        if current_page == "login_existing":

            exist_user = select(
                "",
                [data["user"] for data in login_data]
            )

            if exist_user == "BACK":
                current_page = "login_selection"

            elif exist_user == account["user"]:

                print(
                    f"You are already logged as {exist_user}!"
                )

                account["last_login"] = str(datetime.now())

                dump_login(login_data)

                time.sleep(0.5)

                update_expiry(account["id"])

                return User(
                    user_id,
                    account["user"],
                    account["password"],
                    account["hotel_filter"],
                    account["attractions_filter"],
                    account["reservations_filter"]
                )

            else:

                valid = False

                while not valid:

                    password = input(
                        f"Enter password for {exist_user} >> "
                    )

                    for data in login_data:

                        if (
                            data["user"] == exist_user
                            and
                            data["password"] == password
                        ):

                            valid = True

                            data["last_login"] = str(datetime.now())

                            dump_login(login_data)

                            update_expiry(data["id"])

                            return User(
                                data["id"],
                                data["user"],
                                data["password"],
                                data["hotel_filter"],
                                data["attractions_filter"],
                                data["reservations_filter"]
                            )

                print("Invalid password")


        elif selection == login_type[1]:
            current_page = "register"

        elif selection == login_type[2]:
            current_page = "delete"


        if current_page == "register":

            current_page = "finished"

            return register_user(
                user_id,
                manage_accounts
            )


        if current_page == "delete":

            print_header(
                f"CONFIRM DELETION OF {account['user'].upper()}?"
            )

            confirm_del = select(
                "",
                ["Yes", "No"]
            )

            if confirm_del == "BACK":
                current_page = "login_selection"
                continue

            elif confirm_del == "Yes":
                current_page = "confirm_delete"

            elif confirm_del == "No":

                update_expiry(account["id"])

                return User(
                    user_id,
                    account["user"],
                    account["password"],
                    account["hotel_filter"],
                    account["attractions_filter"],
                    account["reservations_filter"]
                )


        if current_page == "confirm_delete":

            delete_password = input(
                f"Enter password for {account['user']} >> "
            )

            if delete_password.strip() == account["password"]:

                reserve_data = load_reserve()

                clear()

                print(f"{account['user']} deleted")

                time.sleep(0.5)

                reserve_data.remove(
                    next(
                        r for r in reserve_data
                        if r["id"] == user_id
                    )
                )

                login_data.remove(account)

                dump_login(login_data)
                dump_reserve(reserve_data)

                return login_user()


# ============================================================================
# Source: features/payment.py
# ============================================================================
#module name  : payment.py
#date created : 13th August 2026
#created by   : Yap Zi Yi
#imported     : config, json, re (regex), time, datetime, features, helpers.cli_helper, helpers.selection_helper
#amendment    :
#remark       : Payment


# Save transaction history list into the JSON file
def dump_transaction(info):
  with open(TRANSACTION_PATH, "w", encoding="utf-8") as f:
    json.dump(info, f, indent=4)


# Load transaction history from JSON, if file missing or broken reset to empty list
def load_transaction():
  try:
    with open(TRANSACTION_PATH, "r", encoding="utf-8") as f:
      return json.load(f)
  except (json.decoder.JSONDecodeError, FileNotFoundError):
    dump_transaction([])
    return []


# Check card validity using Luhn algorithm
def valid_card(num):  # receives a number in str
  # doubles every even index (index starts at 0), if doubled value > 9, subtract 9 and if all the digits summed is divisible by 10, its a valid card.
  reverse_num = num[::-1]
  new_num = [
      n - 9 if n > 9 else n
      for i, n in enumerate(reverse_num)
      for n in [int(n) * 2 if i % 2 == 1 else int(n)]
  ]
  return sum(new_num) % 10 == 0


# Simple loading spinner animation for payment authorization
def auth_animation():
  clear()
  for i in range(12):
    print(
        f"\rAuthorizing payment {['|', '/', '-', '\\'][i % 4]}",
        end="",
        flush=True,
    )
    time.sleep(0.15)
  print()


# Show main menu for choosing between proceeding to payment, viewing history, or going back
def handle_view_or_pay():
  ui_choices = ["Proceed to payment", "View payment history", "Back"]
  print_header("PAYMENT")
  payment_ui = select("", ui_choices)

  if payment_ui == "BACK" or payment_ui == "Back":
    return "finished"
  elif payment_ui == ui_choices[0]:
    return "proceed_payment"
  elif payment_ui == ui_choices[1]:
    return "view_transaction"
  return "view_or_pay"


# Filter unpaid reservations, format them for selection, and get user's choices
def handle_proceed_payment(account):
  clear()
  reservation_list = []

  prefixes = {
      "hotel": "night(s)",
      "car": "day(s)",
      "attractions": "pax",
  }
  print_header("SELECT RESERVATIONS TO PAY")

  for key, value in account["reservations"].items():
    for reservation in value:
      if not reservation["paid"] and not reservation["expired"]:
        reservation_list.append({
            "reservation_id": reservation["reservation_id"],
            "reservation_type": key.capitalize(),
            "details": reservation["name"],
            "reservation_unit": prefixes[key],
            "reservation_value": reservation[
                prefixes[key].replace("(s)", "s")
            ],
            "net_total": reservation["net_total"],
        })

  if not reservation_list:
    print("There are currently no reservations.")
    input()
    return "view_or_pay", None, None

  reservation_list.sort(key=lambda r: r["reservation_type"])

  reservation_interface = [
      f"{r['reservation_type']} | {r['details']} | {r['reservation_value']}"
      f" {r['reservation_unit']} | RM {r['net_total']:.2f}"
      for r in reservation_list
  ]
  # selected index will have same index as reservation_list

  proceed = checkbox("", reservation_interface)

  if proceed == "BACK":
    return "view_or_pay", None, None
  elif not proceed:
    print("Please select an option. (TAB) ")
    time.sleep(1)
    return "proceed_payment", None, None
  else:
    selected_reservations = [
        reservation_list[reservation_interface.index(r)] for r in proceed
    ]
    selected_id = {sr["reservation_id"] for sr in selected_reservations}
    return "checkout_summary", selected_reservations, selected_id


# Show breakdown of costs including 6% service tax and totals
def handle_checkout_summary(selected_reservations):
  clear()
  subtotal = sum(r["net_total"] for r in selected_reservations)
  taxed = 0.06 * subtotal
  total = subtotal + taxed
  print(f"""
{'─' * 100}
CHECKOUT SUMMARY
{'─' * 100}

RESERVATIONS:
{"\n".join(f"{i+1}. {f'{r["reservation_type"]} : {r["details"]} [{r["reservation_value"]} {r["reservation_unit"]}]':<60} RM {f'{r["net_total"]:.2f}':>8}" for i, r in enumerate(selected_reservations))}

{'─' * 100}
{"Subtotal:":<63} RM {f'{subtotal:.2f}':>8}
{"Service Tax (6%):":<63} RM {f'{taxed:.2f}':>8}
{'─' * 100}
{"Net Total:":<63} RM {f"{total:.2f}":>8}
{'─' * 100}
""")
  confirm_payment = select(
      "Select an option:", ["Choose Payment Method", "Back"]
  )
  if confirm_payment == "BACK" or confirm_payment == "Back":
    return "proceed_payment", total
  elif confirm_payment == "Choose Payment Method":
    return "payment_method", total
  return "checkout_summary", total


# Let user select their preferred payment channel
def handle_payment_method():
  clear()
  print(f"""
{'─' * 60}
SELECT PAYMENT METHOD
{'─' * 60}
""")
  methods = ["Credit / Debit Card", "Online Banking", "E-Wallet", "Back"]
  payment_method = select("", methods)

  if payment_method == "Back" or payment_method == "BACK":
    return "checkout_summary", None
  elif payment_method == methods[0]:
    return "pay_card", payment_method
  elif payment_method == methods[1]:
    return "pay_bank", payment_method
  elif payment_method == methods[2]:
    return "ewallet", payment_method
  return "payment_method", None


# Show list of supported banks for online banking
def handle_pay_bank():
  clear()
  print(f"""
{'─' * 60}
PAYMENT (ONLINE BANKING)
{'─' * 60}
""")
  banks = [
      "Maybank",
      "CIMB Bank",
      "Public Bank",
      "RHB Bank",
      "Hong Leong Bank",
  ]
  select_bank = select("Select Bank\n", banks + ["Back"])

  if select_bank == "BACK" or select_bank == "Back":
    return "payment_method", None
  else:
    return "bank_auth", select_bank


# Prompt user for bank account and PIN, validation included
def handle_bank_auth(select_bank, total):
  clear()
  print(f"""
{'─' * 60}
ONLINE BANKING - {select_bank.upper()}
{'─' * 60}

Amount: RM {total:.2f}
""")
  account_num = input("Enter your bank account number >> ").strip()  # sim
  account_pin = input("Enter your PIN >> ").strip()

  if not account_num:
    return "pay_bank"
  elif not account_num.isdigit() or not (10 <= len(account_num) <= 14):
    auth_animation()
    print("Please enter a valid account number.")
    time.sleep(1)
    return "bank_auth"
  elif not account_pin.isdigit() or not (len(account_pin) == 6):
    auth_animation()
    print("Please enter a valid PIN number.")
    time.sleep(1)
    return "bank_auth"
  else:
    return "payment_success"


# Select from available e-wallet options
def handle_ewallet():
  clear()
  print(f"""
{'─' * 60}
PAYMENT (E-WALLET)
{'─' * 60}
""")
  ewallets = ["Touch 'n Go eWallet", "GrabPay", "Boost", "ShopeePay"]
  select_ewallet = select("Select E-wallet\n", ewallets + ["Back"])

  if select_ewallet == "BACK" or select_ewallet == "Back":
    return "payment_method", None
  else:
    return "ewallet_trans", select_ewallet


# E-wallet transaction confirmation step
def handle_ewallet_trans(select_ewallet, total):
  clear()
  print(f"""
{'─' * 60}
PAYMENT - {select_ewallet.upper()}
{'─' * 60}

Amount: RM {total:.2f}
""")
  input(f"Press ENTER after payment...\n{'─' * 60}\n")
  return "payment_success"


# Prompt and validate card details using regex and Luhn algorithm
def handle_pay_card():
  clear()
  print(f"""
{'─' * 60}
PAYMENT (CREDIT / DEBIT CARD)
{'─' * 60}
""")
  card_num = re.sub(r"\s", "", input("Enter card number >> ")).strip()

  if not card_num:
    return "payment_method"
  elif (
      not (8 <= len(card_num) <= 19)
      or len(card_num) == 17
      or not card_num.isdigit()
      or not valid_card(card_num)
  ):
    auth_animation()
    print("Please enter a valid card.")
    time.sleep(1)
    return "pay_card"
  else:
    return "payment_success"


# Record successful transaction, update paid status, and print receipt
def handle_payment_success(
    trans_acc,
    payment_method,
    selected_reservations,
    total,
    account,
    selected_id,
    transaction_data,
    user_data,
    user_transactions,
):
  auth_animation()
  clear()

  print("\rPayment successful! ✓")
  time.sleep(1.5)

  clear()
  transaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  success_trans = {
      "id": len(trans_acc["transactions"]) + 1,
      "transaction_id": (
          f"TXN-{datetime.now().strftime('%Y%m%d')}-{len(trans_acc['transactions'])+1:04d}"
      ),
      "method": payment_method,
      "date": transaction_time,
      "reservations": [
          f"{r['details']} ({r['reservation_type']})"
          for r in selected_reservations
      ],
      "total": round(total, 2),
  }

  user_transactions.append(success_trans)

  for _, value in account["reservations"].items():
    for r in value:
      if r["reservation_id"] in selected_id:
        r["paid"] = True

  dump_transaction(transaction_data)
  dump_reserve(user_data)

  print(f"""
{'─' * 60}
PAYMENT SUCCESSFUL
{'─' * 60}

{'Receipt #:':<15} {success_trans["transaction_id"]}
{'Date:':<15} {success_trans["date"]}
{'Method:':<15} {success_trans["method"]}

Paid Reservations:
{"• " + "\n• ".join(success_trans["reservations"])}

{'Amount Paid:':<15} RM {success_trans["total"]:.2f}
""")
  input(f"Press enter to return to Payment Menu...\n{'─' * 60}\n")
  return "view_or_pay"


# Show list of user's past transactions and display full receipt details on selection
def handle_view_transaction(trans_acc, user_transactions):
  clear()
  print_header("TRANSACTION HISTORY", 75)

  if not trans_acc["transactions"]:
    print("There are currently no transactions.")
    input()
    return "view_or_pay"

  print(f"""

{'TRANSACTION ID':<20} {'DATE':<20} {'RESERVATIONS':<20} {'TOTAL (RM)':<10}
{'─' * 75}
{"\n".join(f"{trans["transaction_id"]:<20} {trans["date"]:<20} {f'{len(trans["reservations"])} reservation(s)':<20} {f"{trans["total"]:.2f}":<10}" for trans in user_transactions)}

""")
  select_trans = select(
      "Select a transaction to view receipt details, or choose BACK:",
      [t["transaction_id"] for t in user_transactions] + ["Back"],
  )

  if select_trans == "BACK" or select_trans == "Back":
    return "view_or_pay"
  else:
    clear()

    trans_details = next(
        t for t in user_transactions if t["transaction_id"] == select_trans
    )

    print(f"""
{'─' * 60}
TRANSACTION DETAILS
{'─' * 60}

{'Transaction ID:':<15} {trans_details["transaction_id"]}
{'Date:':<15} {trans_details["date"]}
{'Method:':<15} {trans_details["method"]}

Paid Reservations:
{"• " + "\n• ".join(trans_details["reservations"])}

{'─' * 60}
{'Amount Paid:':<15} RM {trans_details["total"]:.2f}
{'─' * 60}

Press ENTER to return...

""")
    input()
    return "view_transaction"


# Main orchestrator function managing the state transitions
def payment(user_id):
  current_page = "view_or_pay"
  user_data = load_reserve()
  transaction_data = load_transaction()
  account = next(data for data in user_data if data["id"] == user_id)

  trans_acc = next(
      (trans for trans in transaction_data if trans["user_id"] == account["id"]),
      None,
  )

  if trans_acc is None:
    trans_acc = {"user_id": account["id"], "transactions": []}
    transaction_data.append(trans_acc)

  user_transactions = trans_acc["transactions"]

  # State variable defaults
  selected_reservations = []
  selected_id = set()
  total = 0.0
  payment_method = ""
  select_bank = ""
  select_ewallet = ""

  while current_page != "finished":
    clear()

    if current_page == "view_or_pay":
      current_page = handle_view_or_pay()
      if current_page == "finished":
        return

    elif current_page == "proceed_payment":
      current_page, sel_res, sel_id = handle_proceed_payment(account)
      if sel_res is not None:
        selected_reservations = sel_res
        selected_id = sel_id

    elif current_page == "checkout_summary":
      current_page, total = handle_checkout_summary(selected_reservations)

    elif current_page == "payment_method":
      current_page, method = handle_payment_method()
      if method:
        payment_method = method

    elif current_page == "pay_bank":
      current_page, bank = handle_pay_bank()
      if bank:
        select_bank = bank

    elif current_page == "bank_auth":
      current_page = handle_bank_auth(select_bank, total)

    elif current_page == "ewallet":
      current_page, wallet = handle_ewallet()
      if wallet:
        select_ewallet = wallet

    elif current_page == "ewallet_trans":
      current_page = handle_ewallet_trans(select_ewallet, total)

    elif current_page == "pay_card":
      current_page = handle_pay_card()

    elif current_page == "payment_success":
      current_page = handle_payment_success(
          trans_acc,
          payment_method,
          selected_reservations,
          total,
          account,
          selected_id,
          transaction_data,
          user_data,
          user_transactions,
      )

    elif current_page == "view_transaction":
      current_page = handle_view_transaction(trans_acc, user_transactions)


# ============================================================================
# Source: features/hotel.py
# ============================================================================
#module name  : hotel.py
#date created : 15th August 2026
#created by   : Yap Zi Yi
#imported     : features, helpers.selection_helper, config, helpers.cli_helper, json, textwrap, features.payment, datetime, math, helpers.availability_helper, helpers.login_helper
#amendment    :
#remark       : Hotel Reservations 


def rating(HotelRating):

    ratings = ["one", "two", "three", "four", "five"]

    # Since "S" in Star from any OneStar, TwoStar, ThreeStar, is at index -4,
    # we can just slice it till the letter before 's'
    return "★" * (ratings.index(HotelRating.lower()[:-4]) + 1) if HotelRating.lower()[:-4] in ratings else "N/A"


def apply_filter(data, city, user_filter):
 # Filters hotels by city and sorts them according to the selected filter.
    city_hotels = data[data["cityName"] == city]

    if user_filter == "Default":
        pass

    elif user_filter == "Price: Low → High":
        city_hotels = city_hotels.sort_values("price")

    elif user_filter == "Price: High → Low":
        city_hotels = city_hotels.sort_values("price", ascending=False)

    elif user_filter == "Rating: Low → High":
        city_hotels = city_hotels.sort_values(
            by="HotelRating",
            key=lambda series: series.map(
                lambda r: len(rating(r)) if rating(r) != "N/A" else 0 
            )
        )

    elif user_filter == "Rating: High → Low":
        city_hotels = city_hotels.sort_values(
            by="HotelRating",
            key=lambda series: series.map(
                lambda r: len(rating(r)) if rating(r) != "N/A" else 0
            ),
            ascending=False
        )

    elif user_filter == "Name: A → Z":
        city_hotels = city_hotels.sort_values("HotelName")

    return city_hotels.reset_index(drop=True)


def select_hotel(city_hotels, availability, city):
# Displays available hotels and returns the hotel selected by the user.
    choices = [
        (f"{f'{i+1}.':<5} {data['HotelName']:<115} | {rating(data['HotelRating']):<5} | RM {data['price']:.2f}")
        for i, data in city_hotels.iterrows()
    ]

    clear()
    print_header(f"HOTELS IN {city.upper()}")

    hotel = search("", choices, 10)

    if hotel == "BACK":
        return None

    elif hotel is not None:

        choice_index = choices.index(hotel)
        hotel_details = city_hotels.iloc[choice_index]
        hotel_name = hotel_details["HotelName"]

        if availability[hotel_name] == 0:
            print("Oops! It seems that the hotel you were looking for is fully booked. We are sorry for the inconvenience.")
            input()
            return None

        return hotel_details

    return None


def select_dates():
# Gets and validates the reservation start and end dates from the user.
    clear()
    valid_date = False
    print_header("HOTEL RESERVATION PERIOD")

    while not valid_date:

        try:
            start_input = input("Enter start date (DD/MM/YYYY) >> ").strip()
            end_input = input("Enter end date (DD/MM/YYYY) >> ").strip()

            if not start_input or not end_input:
                return None

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
            return start, end, start_input, end_input, nights


def reserve_hotel(user_id):
# Handles the hotel reservation process from searching for a hotel to confirming the reservation.
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

            browse_selection = [
                "Browse hotels",
                "Change filters",
                "Reset filters",
                "Back"
            ]

            browse_or_sort = select("", browse_selection)

            if browse_or_sort == "BACK" or browse_or_sort == "Back":
                current_page = "finished"
                return

            elif browse_or_sort == browse_selection[0]:
                current_page = "hotel_selection"

            elif browse_or_sort == browse_selection[1]:
                current_page = "change_filters"

            elif browse_or_sort == browse_selection[2]:
                city_hotels = hotel_data[
                    hotel_data["cityName"] == account["city"]
                ].reset_index(drop=True)

                user_filter = "Default"


        if current_page == "change_filters":

            clear()
            print_header("SELECT FILTER")

            filter_choices = [
                "Default",
                "Price: Low → High",
                "Price: High → Low",
                "Rating: Low → High",
                "Rating: High → Low",
                "Name: A → Z",
                "Back"
            ]

            new_filter = select("Sort by:", filter_choices)

            if new_filter == "BACK" or new_filter == "Back":
                current_page = "hotel_search"
                continue

            else:
                user_filter = new_filter

                city_hotels = apply_filter(
                    hotel_data,
                    account["city"],
                    user_filter
                )

                account_login["hotel_filter"] = user_filter
                dump_login(user_login)

                current_page = "hotel_search"


        if current_page == "hotel_selection":

            hotel_details = select_hotel(
                city_hotels,
                availability,
                account["city"]
            )

            if hotel_details is None:
                current_page = "hotel_search"

            else:

                hotel_name = hotel_details["HotelName"]
                hotel_rating = rating(hotel_details["HotelRating"])
                hotel_address = hotel_details["Address"]
                hotel_desc = json.loads(hotel_details["Description"])
                hotel_facilities = json.loads(hotel_details["HotelFacilities"])
                hotel_price = hotel_details["price"]
                hotel_fax = hotel_details["FaxNumber"]
                hotel_phone = hotel_details["PhoneNumber"]
                hotel_website = hotel_details["HotelWebsiteUrl"]

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

            confirm_reserve = select(
                "",
                ["Continue", "View full details", "Back"]
            )

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
                current_page = "select_room"


        if current_page == "select_room":

            room_list = [
                "Single Room",
                "Double Room",
                "Triple Room",
                "Family Room"
            ]

            print_header("SELECT ROOM TYPE")

            room_type = select(
                "",
                room_list + ["Back"]
            )

            if room_type == "BACK":
                current_page = "confirm_reservation"
                continue

            else:
                selected_room_type = room_type.lower().split()[0]
                current_page = "num_rooms"


        if current_page == "num_rooms":

            num_rooms = input(
                f"Enter the number of rooms to reserve for {room_type} "
                f"(Available rooms: {availability[hotel_name]}) >> "
            ).strip()

            if not num_rooms:
                current_page = "select_room"

            elif not num_rooms.isdigit() or int(num_rooms) <= 0:
                print(
                    "Number of rooms must be an integer and not less than or equal to zero."
                )

            elif int(num_rooms) > availability[hotel_name]:
                print(
                    "Number of rooms cannot exceed the hotel's maximum room capacity."
                )

            elif num_rooms.isdigit():

                if int(num_rooms) > 7:

                    confirmation = select(
                        f"Are you sure you want to reserve {num_rooms} rooms?",
                        ["Yes", "No"]
                    )

                    if confirmation == "No" or confirmation == "BACK":
                        continue

                num_rooms = int(num_rooms)

                current_page = "date"


        if current_page == "date":

            dates = select_dates()

            if dates is None:
                current_page = "select_room"

            else:
                start, end, start_input, end_input, nights = dates
                current_page = "reserved"


        if current_page == "reserved":

            guest_multiplier = (
                0.364 * math.log(room_list.index(room_type) + 1) + 1
            )

            net_total = round(
                guest_multiplier *
                hotel_details["price"] *
                num_rooms *
                nights,
                2
            )

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

            confirm = select(
                "Confirm reservation? >> ",
                ["Yes", "No"]
            )

            if confirm == "Yes":

                print("\nReserved!\n")

                total_reservations = (
                    sum(len(v) for v in account["reservations"].values()) + 1
                )

                account["reservations"]["hotel"].append(
                    {
                        "reservation_id": total_reservations,
                        "name": hotel_details["HotelName"],
                        "city": account["city"],
                        "rating": len(rating(hotel_details["HotelRating"])),
                        "start": str(start),
                        "end": str(end),
                        "nights": int(nights),
                        "room_type": selected_room_type,
                        "rooms": int(num_rooms),
                        "base_price": float(hotel_details["price"]),
                        "net_total": float(net_total),
                        "paid": False,
                        "expired": False
                    }
                )

                availability[hotel_name] -= num_rooms

                dump_availability(availability)
                dump_reserve(user_data)

                options = [
                    "Proceed to checkout",
                    "Continue with another reservation",
                    "Quit"
                ]

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


# ============================================================================
# Source: features/car.py
# ============================================================================
#module name  : car.py
#date created : 13th August 2026
#created by   : 
#imported     : features, helpers.selection_helper, config, datetime, features.payment, helpers.cli_helper
#amendment    :
#remark       : Car reservation


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

        no_of_days = (end - start).days+ 1

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


# ============================================================================
# Source: features/attractions.py
# ============================================================================
#module name  : attractions.py
#date created : 19th August 2026
#created by   : Yap Zi Yi
#imported     : features, helpers.login_helper, helpers.selection_helper, helpers.cli_helper, config, datetime, features.payment, time
#amendment    :
#remark       : Attractions Reservations 

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

        days = (end - start).days +1

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


# ============================================================================
# Source: features/reservations.py
# ============================================================================
#module name  : reservations.py
#date created : 24th August 2026
#created by   : Yap Zi Yi
#imported     : features, helpers.selection_helper, helpers.cli_helper, helpers.login_helper
#amendment    :
#remark       : Reservations 



def get_city_reservations(data, city):
    return {
        key: [v for v in value if v["city"] == city]
        for key, value in data.items()
    }


def apply_filter(data, user_filter):
    if user_filter == "Default":
        return data

    if user_filter == "Hotel":
        return {"hotel": data["hotel"]}

    if user_filter == "Car":
        return {"car": data["car"]}

    if user_filter == "Attractions":
        return {"attractions": data["attractions"]}

    if user_filter == "Paid":
        return {
            key: [
                r for r in reservations
                if r["paid"] and not r["expired"]
            ]
            for key, reservations in data.items()
        }

    if user_filter == "Unpaid":
        return {
            key: [
                r for r in reservations
                if not r["paid"] and not r["expired"]
            ]
            for key, reservations in data.items()
        }

    if user_filter == "Expired":
        return {
            key: [
                r for r in reservations
                if r["expired"]
            ]
            for key, reservations in data.items()
        }

    return data


def print_reservations(data):

    prefixes = {
        "hotel": "night(s)",
        "car": "day(s)",
        "attractions": "pax",
    }

    if not any(data.values()):
        print("There are currently no reservations.")
        input()
        return False

    for reservation_type, reservations in data.items():

        if not reservations:
            continue

        print(f"""

{reservation_type.upper()}
{'─' * 60}
{"\n".join(
    f'{r["name"]}\n'
    f'{r["start"]} -> {r["end"]}\n'
    f'{r[prefixes[reservation_type].replace("(s)", "s")]} '
    f'{prefixes[reservation_type]} | '
    f'RM {r["net_total"]:.2f} | '
    f'{"PAID" if r["paid"] else "UNPAID"}'
    for r in reservations
)}
""")

    return True


def select_reservation(data):

    reservation_list = []

    for reservation_type, reservations in data.items():

        for reservation in reservations:

            reservation_list.append({
                "type": reservation_type,
                "reservation": reservation
            })

    choices = [
        f'{r["reservation"]["name"]} '
        f'({r["type"].capitalize()})'
        for r in reservation_list
    ]

    choices.append("Back")

    selected = select(
        "Select a reservation:",
        choices
    )

    if selected == "Back" or selected == "BACK":
        return None

    index = choices.index(selected)

    return reservation_list[index]


def print_reservation_details(reservation, reservation_type):

    prefixes = {
        "hotel": "night(s)",
        "car": "day(s)",
        "attractions": "pax",
    }

    value_key = prefixes[reservation_type].replace("(s)", "s")

    print(f"""
{'Name:':<20} {reservation["name"]}
{'City:':<20} {reservation["city"]}
{'Period':<20} {reservation["start"]} -> {reservation["end"]}
{value_key.capitalize() + ":":<20} {reservation[value_key]}
{'Payment:':<20} {"PAID" if reservation["paid"] else "UNPAID"}
{'Total:':<20} RM {reservation["net_total"]:.2f}

{'─' * 60}
""")


def reservations(user_id):

    current_page = "view"

    reservation_datas = load_reserve()
    user_login = load_login()

    account_login = next(
        data for data in user_login
        if data["id"] == user_id
    )

    account = next(
        data for data in reservation_datas
        if data["id"] == user_id
    )

    user_filter = account_login["reservations_filter"]

    city_reservations = get_city_reservations(
        account["reservations"],
        account["city"]
    )

    user_reservations = apply_filter(
        city_reservations,
        user_filter
    )

    while current_page != "finished":

        # RESERVATION MENU

        if current_page == "view":

            clear()

            ui_choices = [
                "View Reservations",
                "Change Filter",
                "Reset Filter",
                "Back"
            ]

            print_header("RESERVATIONS")
            print(f"Filter: {user_filter}")
            print(f"City: {account['city']}")

            reservation_ui = select("", ui_choices)

            if reservation_ui == "BACK" or reservation_ui == "Back":

                current_page = "finished"
                return

            elif reservation_ui == "View Reservations":

                current_page = "view_reservations"

            elif reservation_ui == "Change Filter":

                current_page = "change_filter"

            elif reservation_ui == "Reset Filter":

                current_page = "reset_filter"


        # VIEW RESERVATIONS

        if current_page == "view_reservations":

            clear()

            print_header("VIEW RESERVATIONS")

            valid = print_reservations(
                user_reservations
            )

            if not valid:

                current_page = "view"
                continue

            selected_reservation = select_reservation(
                user_reservations
            )

            if selected_reservation is None:

                current_page = "view"

            else:

                reservation = selected_reservation["reservation"]
                reservation_type = selected_reservation["type"]

                current_page = "reservation_details"


        # CHANGE FILTER

        if current_page == "change_filter":

            clear()

            print_header("SELECT FILTER")

            filters = [
                "Default",
                "Paid",
                "Unpaid",
                "Expired",
                "Hotel",
                "Car",
                "Attractions"
            ]

            new_filter = select(
                "Filter by:",
                filters + ["Back"]
            )

            if new_filter == "Back" or new_filter == "BACK":

                current_page = "view"
                continue

            user_filter = new_filter

            account_login["reservations_filter"] = user_filter

            dump_login(user_login)

            user_reservations = apply_filter(
                city_reservations,
                user_filter
            )

            current_page = "view"

        if current_page == "reset_filter":
            user_filter = account_login["reservations_filter"] = "Default"
            user_reservations = apply_filter(
                    city_reservations,
                    user_filter
                )

            dump_login(user_login)
            current_page = "view"
            


        # RESERVATION DETAILS

        if current_page == "reservation_details":

            clear()

            print_header("RESERVATION DETAILS")

            print_reservation_details(
                reservation,
                reservation_type
            )

            detail_choices = [
                "Cancel Reservation",
                "Back"
            ]

            detail_ui = select(
                "Select an option:",
                detail_choices
            )

            if detail_ui == "Cancel Reservation":

                current_page = "cancel_confirmation"

            elif detail_ui == "Back" or detail_ui == "BACK":

                current_page = "view_reservations"


        # CANCEL CONFIRMATION

        if current_page == "cancel_confirmation":

            clear()

            print_header("CANCEL RESERVATION")

            print(f"""
Reservation ID:  {reservation["reservation_id"]}
Name:            {reservation["name"]}
City:            {reservation["city"]}
Start:           {reservation["start"]}
End:             {reservation["end"]}
Total:           RM {reservation["net_total"]:.2f}
Payment:         {"PAID" if reservation["paid"] else "UNPAID"}

Are you sure you want to cancel this reservation?
""")

            confirm = select(
                "Select an option:",
                [
                    "Yes, cancel reservation",
                    "No, keep reservation"
                ]
            )

            if confirm == "Yes, cancel reservation":

                current_page = "cancel_reservation"

            else:

                current_page = "reservation_details"


        # CANCEL RESERVATION

        if current_page == "cancel_reservation":

            clear()

            print_header("CANCEL RESERVATION")

            for reservations_list in account["reservations"].values():

                if reservation in reservations_list:

                    reservations_list.remove(reservation)
                    break

            dump_reserve(reservation_datas)

            print("Reservation cancelled successfully! ✓")

            input("Press ENTER to return...\n")

            # Refresh reservations after deletion

            city_reservations = get_city_reservations(
                account["reservations"],
                account["city"]
            )

            user_reservations = apply_filter(
                city_reservations,
                user_filter
            )

            current_page = "view"


# ============================================================================
# Source: main.py
# ============================================================================
#module name  : main.py
#date created : 9th August 2026
#created by   : 
#imported     : select, login_user, manage_acccounts, reserve_hotel, reserve_car, switch_city, reserve_attraction, payment, reservations, clear
#amendment    :
#remark       : Main Menu


user = login_user()

def menu_interface():
    global user
    menu_options = ["Reserve Hotel", "Reserve Car", "Reserve Attractions", "Reservations", "Payment", "Switch City", "Manage Accounts", "Quit"]
    menu = True

    redirect = {
        "Reserve Hotel": reserve_hotel,
        "Reserve Car": reserve_car,
        "Reserve Attractions": reserve_attraction,
        "Reservations" : reservations,
        "Payment": payment,
        "Switch City": switch_city,
        "Manage Accounts": manage_accounts,
    }
    
    while menu:
        clear()
        try:
            user_input = select(
                f"\n{'─'*60}\n        TRAVEL RESERVATION SYSTEM\n{'─'*60}\n\n"
                f"Logged in as: {user.user}\nCurrent city: {user.city}\n",
                menu_options
            )

            # Escape handling – go back to the menu without error
            if user_input == "BACK":
                continue

            if user_input == "Quit":
                clear()
                menu = False
                break

            if user_input == "Switch City":
                user.city = switch_city(user.id)
                continue

            # Call the appropriate feature; if it returns a user object, update it
            result = redirect.get(user_input)
            if result:
                updated = result(user.id)
                if updated is not None:
                    user = updated
            continue
        except KeyboardInterrupt:
            continue

menu_interface()
