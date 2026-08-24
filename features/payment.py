from features import load_reserve, dump_reserve
from helpers.selection_helper import select, checkbox
from helpers.cli_helper import clear, print_header
from datetime import datetime
import time
from config import TRANSACTION_PATH
import json
import re

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

def valid_card(num): # receives a number in str
    # doubles every even index (index starts at 0), if doubled value > 9, subtract 9 and if all the digits summed is divisible by 10, its a valid card.
    reverse_num = num[::-1]
    new_num = [n - 9 if n > 9 else n for n in [int(n) * 2 if i % 2 == 1 else int(n) for i, n in enumerate(reverse_num)]]
    return sum(new_num) % 10 == 0 

def auth_animation():
    clear()
    for i in range(12):
        print(f"\rAuthorizing payment {['|', '/', '-', '\\'][i % 4]}", end="", flush=True)
        time.sleep(0.15)
    print()

def payment(user_id):
    current_page = "view_or_pay"
    user_data = load_reserve()
    transaction_data = load_transaction()
    account = next(data for data in user_data if data["id"] == user_id)
    


    trans_acc = next((trans for trans in transaction_data if trans["user_id"] == account["id"]), None)

    if trans_acc is None:
        trans_acc = {
            "user_id" : account["id"],
            "transactions" : []
        }

        transaction_data.append(trans_acc)
    user_transactions = trans_acc["transactions"]

    while current_page != "finished":
        clear()
        if current_page == "view_or_pay":
            ui_choices = ["Proceed to payment", "View payment history", "Back"]
            print_header("PAYMENT")
            payment_ui = select("", ui_choices)

            if payment_ui == "BACK" or payment_ui == "Back":
                current_page = "finished"
                return
            elif payment_ui == ui_choices[0]:
                current_page = "proceed_payment"
            elif payment_ui == ui_choices[1]:
                current_page = "view_transaction"


        if current_page == "proceed_payment":
            clear()
            reservation_list = []

            prefixes = {
                "hotel": "night(s)",
                "car": "day(s)",
                "attractions": "pax"
            }
            print_header("SELECT RESERVATIONS TO PAY")
            
            for key, value in account["reservations"].items():
                for reservation in value:
                    if not reservation["paid"]:
                        reservation_list.append(
                            {
                                "reservation_id" : reservation["reservation_id"],
                                "reservation_type" : key.capitalize(),
                                "details" : reservation["name"],
                                "reservation_unit" : prefixes[key],
                                "reservation_value" : reservation[prefixes[key].replace("(s)", "s")],
                                "net_total" : reservation["net_total"]
                            }
                        )

            if not reservation_list:
                print("There are currently no reservations.")
                input()
                current_page = "view_or_pay"
                continue

            reservation_list.sort(key = lambda r: r["reservation_type"])

            reservation_interface = [f"{r["reservation_type"]} | {r["details"]} | {r["reservation_value"]} {r["reservation_unit"]} | RM {r["net_total"]:.2f}" for r in reservation_list]
            #selected index will have same index as reservation_list

            proceed = checkbox("", reservation_interface)

            if proceed == "BACK":
                current_page = "view_or_pay"
            elif not proceed:
                print("Please select an option. (TAB) ")
                time.sleep(1)
                continue
            else:
                selected_reservations = [reservation_list[reservation_interface.index(r)] for r in proceed]
                selected_id = {sr["reservation_id"] for sr in selected_reservations}
                current_page = "checkout_summary"

        if current_page == "checkout_summary":
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
            confirm_payment = select("Select an option:", ["Choose Payment Method", "Back"])
            if confirm_payment == "BACK" or confirm_payment == "Back":
                current_page = "proceed_payment"
            elif confirm_payment == "Choose Payment Method":
                current_page = "payment_method"

        if current_page == "payment_method":
            clear()
            print(f"""
{'─' * 60}
SELECT PAYMENT METHOD
{'─' * 60}
""")
            methods = ["Credit / Debit Card", "Online Banking", "E-Wallet", "Back"]
            payment_method = select("", methods)

            if payment_method == "Back" or payment_method == "BACK":
                current_page = "checkout_summary"
            elif payment_method == methods[0]:
                current_page = "pay_card"
            elif payment_method == methods[1]:
                current_page = "pay_bank"
            elif payment_method == methods[2]:
                current_page = "ewallet"
        
        if current_page == "pay_bank":
            clear()
            print(f"""
{'─' * 60}
PAYMENT (ONLINE BANKING)
{'─' * 60}
""")

            banks = ["Maybank", "CIMB Bank", "Public Bank", "RHB Bank", "Hong Leong Bank"]

            select_bank = select("Select Bank\n", banks + ["Back"])

            if select_bank == "BACK" or select_bank == "Back":
                current_page = "payment_method"
            else:
                current_page = "bank_auth"

        if current_page == "bank_auth":
            clear()
            print(f"""
{'─' * 60}
ONLINE BANKING - {select_bank.upper()}
{'─' * 60}

Amount: RM {total:.2f}
""")

            account_num = input("Enter your bank account number >> ").strip() #sim
            account_pin = input("Enter your PIN >> ").strip()
            if not account_num:
                current_page = "pay_bank"
            elif not account_num.isdigit() or not (10 <= len(account_num) <= 14):
                auth_animation()
                print("Please enter a valid account number.")
                time.sleep(1)
            elif not account_pin.isdigit() or not (len(account_pin) == 6):
                auth_animation()
                print("Please enter a valid PIN number.")
                time.sleep(1)
            else:
                current_page = "payment_success"

            
        if current_page == "ewallet":
            clear()
            print(f"""
{'─' * 60}
PAYMENT (E-WALLET)
{'─' * 60}
""")
            ewallets = ["Touch 'n Go eWallet", "GrabPay", "Boost", "ShopeePay"]
            
            select_ewallet = select("Select E-wallet\n", ewallets + ["Back"])
            
            if select_ewallet == "BACK" or select_ewallet == "Back":
                current_page = "payment_method"
            else:
                current_page = "ewallet_trans"

        if current_page == "ewallet_trans":
            clear()
            print(f"""
{'─' * 60}
PAYMENT - {select_ewallet.upper()}
{'─' * 60}

Amount: RM {total:.2f}
""")

            input(f"Press ENTER after payment...\n{'─' * 60}\n")
            current_page = "payment_success"

        if current_page == "pay_card":
            clear()
            print(f"""
{'─' * 60}
PAYMENT (CREDIT / DEBIT CARD)
{'─' * 60}
""")
            card_num = re.sub(r"\s", "", input("Enter card number >> ")).strip()
            if not card_num:
                current_page = "payment_method"
            elif not (8 <= len(card_num) <= 19) or len(card_num) == 17 or not card_num.isdigit() or not valid_card(card_num):
                auth_animation()
                print("Please enter a valid card.")
                time.sleep(1)
            else:
                current_page = "payment_success"
        
        if current_page == "payment_success":
            #animation
            auth_animation()
            clear()

            print("\rPayment successful! ✓")
            time.sleep(1.5)

            clear()
            transaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            success_trans = {
                    "id" : len(trans_acc["transactions"]) + 1,
                    "transaction_id" : f"TXN-{datetime.now().strftime("%Y%m%d")}-{len(trans_acc["transactions"])+1:04d}",
                    "method" : payment_method,
                    "date" : transaction_time,
                    "reservations" : [f"{r["details"]} ({r["reservation_type"]})"for r in selected_reservations],
                    "total" : round(total,2)
                }

        
            user_transactions.append(success_trans)

            for key, value in account["reservations"].items():
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
            current_page = "view_or_pay"


        if current_page == "view_transaction":
            clear()
            print_header("TRANSACTION HISTORY", 75)
            if not trans_acc["transactions"]:
                print("There are currently no transactions.")
                input()
                current_page = "view_or_pay"
                continue
    
            print(f"""

{'TRANSACTION ID':<20} {'DATE':<20} {'RESERVATIONS':<20} {'TOTAL (RM)':<10}
{'─' * 75}
{"\n".join(f"{trans["transaction_id"]:<20} {trans["date"]:<20} {f'{len(trans["reservations"])} reservation(s)':<20} {trans["total"]:<10}" for trans in user_transactions)}

""")
            select_trans = select("Select a transaction to view receipt details, or choose BACK:", [t["transaction_id"] for t in user_transactions] + ["Back"])

            if select_trans == "BACK" or select_trans == "Back":
                current_page = "view_or_pay"
            else:
                clear()

                trans_details = next(t for t in user_transactions if t["transaction_id"] == select_trans)

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