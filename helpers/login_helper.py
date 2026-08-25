import json
import re
import time
from datetime import datetime, timedelta
from config import LOGIN_PATH
from user_class import User
from helpers.selection_helper import select
from helpers.cli_helper import clear, print_header
from features import load_reserve, dump_reserve
from helpers.expiry_helper import check_expired_reservations


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