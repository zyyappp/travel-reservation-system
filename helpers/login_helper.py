import json
import re
import time
from datetime import datetime, timedelta
from config import LOGIN_PATH
from user_class import User
from helpers.selection_helper import select, search
from helpers.cli_helper import clear
from features import load_reserve, dump_reserve

def load_login():
    with open(LOGIN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def dump_login(info):
    with open(LOGIN_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)


def register_user(user_id = None, previous_page=None):
    clear()
    print(f"""
{'─' * 60}
                       CREATE ACCOUNT
{'─' * 60}
""")
    login_data = load_login()
    user_valid = False
    password_valid = False
    while not user_valid:

        username = input("Enter username >> ")

        if username == "":

            if previous_page is None:
                continue
            else:
                clear()
                return previous_page(user_id)

        elif len(username) <3:
            print("Username must be greater than 2 in length")
            continue

        elif re.search(r"\s", username):
            print("Username must not include spaces")
            continue


        if username in [data["user"] for data in load_login()]:
            print("Username already exists")
            continue

        user_valid = True

    while not password_valid:
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

        password_valid = True
    
    data = {
        "id" : len(login_data) + 1,
        "user" : username,
        "password" : password,
        "date_created" : str(datetime.now()),
        "last_login" : str(datetime.now())
    }
    login_data.append(data)
    dump_login(login_data)

    return User(data["id"], username, password)


def login_user(user_id = None):
    login_data = load_login()
    if not login_data:
        print(f"{"-"*20}\nRegister\n{"-" * 20}")
        return register_user()

    earliest_login = None
    for i, login in enumerate(login_data):
        now = datetime.now()
        login_time = datetime.strptime(login["last_login"], "%Y-%m-%d %H:%M:%S.%f")
        time_diff = now - login_time

        if time_diff <= timedelta(minutes=15):
            if earliest_login is None:
                earliest_login = i

            elif (time_diff < (now - datetime.strptime(login_data[earliest_login]["last_login"], "%Y-%m-%d %H:%M:%S.%f"))):
                earliest_login = i

    if earliest_login is None:
        #login
        clear()
        current_page = "reg_or_login"

        while current_page != "finished":

            if current_page == "reg_or_login":
                clear()
                reg_or_login = select("Register or Login", ["Login to existing account", "Register a new account"])


                if reg_or_login == "BACK":
                    current_page = "reg_or_login"
                if reg_or_login == "Register a new account":
                    current_page = "finished"
                    return register_user(previous_page=login_user)
                if reg_or_login == "Login to existing account":
                    current_page = "login"

            if current_page == "login":
                print(f"{"-"*20}\nLogin\n{"-" * 20}")
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
                        return User(log["id"], username, password)
                print("Invalid username or password.")
                time.sleep(0.5)
                

    else:
        latest_login = login_data[earliest_login]
        latest_login["last_login"] = str(datetime.now())
        dump_login(login_data)
        return User(latest_login["id"], latest_login["user"], latest_login["password"])


def manage_accounts(user_id):

    current_page = "login_selection"
    login_data = load_login()

    account = next(
        data for data in login_data if data["id"] == user_id
    )

    while current_page != "finished":
        login_type =  ["Login to existing account", "Add a new account", "Delete account"]
        selection = select("--- Login ---", login_type)

        if selection == "BACK":
            current_page = "finished"
            return User(user_id, account["user"], account["password"])

        if selection == login_type[0]:
            current_page = "login_existing"

        if current_page == "login_existing":
            exist_user = select("", [data["user"] for data in login_data])
            if exist_user == "BACK":
                current_page = "login_selection"
            elif exist_user == account["user"]:
                print(f"You are already logged as {exist_user}!")
                account["last_login"] = str(datetime.now())
                dump_login(login_data)
                time.sleep(0.5)
                return User(user_id, account["user"], account["password"])
            else:
                valid = False
                while not valid:
                    password = input(f"Enter password for {exist_user} >> ")

                    for data in login_data:
                        if data["user"] == exist_user and data["password"] == password:
                            valid = True
                            data["last_login"] = str(datetime.now())
                            dump_login(login_data)
                            return User(data["id"], data["user"], data["password"])

                
                print("Invalid password")
        elif selection == login_type[1]:
            current_page = "register"
        elif selection == login_type[2]:
            current_page = "delete"

        if current_page == "register":
            current_page = "finished"
            return register_user(user_id, manage_accounts)

        if current_page == "delete":
            confirm_del = select(f"Confirm deletion of {account["user"]}?", ["Yes", "No"])

            if confirm_del == "BACK":
                current_page = "login_selection"
                continue
            elif confirm_del == "Yes":
                current_page = "confirm_delete"

            elif confirm_del == "No":
                return User(user_id, account["user"], account["password"])

        if current_page == "confirm_delete":
            delete_password = input(f"Enter password for {account["user"]} >> ")

            if delete_password.strip() == account["password"]:
                reserve_data = load_reserve()
                clear()
                print(f"{account["user"]} deleted")
                time.sleep(0.5)

                reserve_data.remove(next(r for r in reserve_data if r["id"] == user_id))
                login_data.remove(account)
                dump_login(login_data)
                dump_reserve(reserve_data)
                return login_user()