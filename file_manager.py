import json
import re
import subprocess
import time
from datetime import datetime
from config import LOGIN_PATH

def load_login():
    with open(LOGIN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def dump_login(info):
    with open(LOGIN_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)


def register_user():
    login_data = load_login()
    subprocess.run("cls", shell=True)
    user_valid = False
    password_valid = False
    while not user_valid:

        username = input("Enter username >> ")

        if len(username) > 3:
            user_valid = True
            break
        else:
            print("Username must be greater than 3 characters")
            time.sleep(0.5)

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
    if not load_login():
        register_user()