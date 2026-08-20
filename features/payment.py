from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select, checkbox
from helpers.cli_helper import clear
from datetime import datetime
import time
from config import TRANSACTION_PATH
import json

def dump_transaction(info):
    with open(TRANSACTION_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)

def load_transaction():
    try:
        with open(TRANSACTION_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        dump_transaction([])
        return []

def payment(user_id):
    current_page = "view_or_pay"
    user_data = load_reserve()
    account = next(data for data in user_data if data["id"] == user_id)

    while current_page != "finished":
        clear()
        if current_page == "view_or_pay":
            ui_choices = ["Proceed to payment", "View payment history"]
            print(f"""
        {'─' * 60}
        PAYMENT
        {'─' * 60}
        """)
            payment_ui = select("", ui_choices)

            if payment_ui == "BACK":
                current_page = "finished"
                return
            elif payment_ui == ui_choices[0]:
                current_page = "proceed_payment"
            elif payment_ui == ui_choices[1]:
                current_page = "view_transaction"


        if current_page == "proceed_payment":
            reservation_list = [f"{key.capitalize()} | {value[i]["name"]} | {"Paid" if value[i]["paid"] else "Unpaid"}"for key, value in account["reservations"].items() for i in range(len(value))]
            proceed = checkbox("", reservation_list)
        if current_page == "view_transaction":
            pass