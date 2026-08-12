import json
import re
import subprocess
import time
from datetime import datetime, timedelta
from config import LOGIN_PATH

def load_login():
    with open(LOGIN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def dump_login(info):
    with open(LOGIN_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)


def register_user():
    login_data = load_login()
    user_valid = False
    password_valid = False
    while not user_valid:

        username = input("Enter username >> ").strip()

        if len(username) <=3:
            print("Username must be greater than 3 in length")
            continue

        if re.search(r"\s", username):
            print("Username must not include spaces")
            continue

        user_valid = True

    while not password_valid:
        password = input("Enter password >> ").strip()

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
        "user" : username,
        "password" : password,
        "date_created" : str(datetime.now()),
        "last_login" : str(datetime.now())
    }
    login_data.append(data)
    dump_login(login_data)


def login_user():
    login_data = load_login()
    if not login_data:
        print(f"{"-"*20}\nRegister\n{"-" * 20}")
        register_user()
        return True
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
        subprocess.run("cls", shell=True)
        success = False
        print(f"{"-"*20}\nLogin\n{"-" * 20}")
        while not success:
            username = input("Enter username >> ")
            password = input("Enter password >> ")

            for log in login_data:
                if log["user"] == username and log["password"] == password:
                    success = True

                    log["last_login"] = str(datetime.now())
                    dump_login(login_data)
                    return success
            if not success:
                print("Username or password entered is incorrect or does not exist.")
    else:
        login_data[earliest_login]["last_login"] = str(datetime.now())
        dump_login(login_data)
        return True
        