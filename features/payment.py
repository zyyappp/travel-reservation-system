#module name  : payment.py
#date created : 13th August 2026
#created by   : Yap Zi Yi
#imported     : config, json, re (regex), time, datetime, features, helpers.cli_helper, helpers.selection_helper
#amendment    :
#remark       : Payment
import json
import re
import time
from datetime import datetime
from config import TRANSACTION_PATH
from features import dump_reserve, load_reserve
from helpers.cli_helper import clear, print_header
from helpers.selection_helper import checkbox, select


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
      f"{r['reservation_type']} | Reservation #{r['reservation_id']} | {r['details']} | {r['reservation_value']}"
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
  print_header("SELECT PAYMENT METHOD")
  methods = ["Credit / Debit Card", "Online Banking", "E-Wallet"]
  payment_method = select("", methods + ["Back"])

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
  print_header("PAYMENT (ONLINE BANKING)")
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
  print_header("PAYMENT (E-WALLET)")
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
  print_header("PAYMENT (CREDIT / DEBIT CARD)")
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
    user_transactions
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
  payment_method = select_bank = select_ewallet =  ""

  while current_page != "finished":
    clear()

    if current_page == "view_or_pay":
      current_page = handle_view_or_pay()
      if current_page == "finished":
        return

    if current_page == "proceed_payment":
      current_page, sel_res, sel_id = handle_proceed_payment(account)
      if sel_res is not None:
        selected_reservations = sel_res
        selected_id = sel_id

    if current_page == "checkout_summary":
      current_page, total = handle_checkout_summary(selected_reservations)

    if current_page == "payment_method":
      current_page, method = handle_payment_method()
      if method:
        payment_method = method

    if current_page == "pay_bank":
      current_page, bank = handle_pay_bank()
      if bank:
        select_bank = bank

    if current_page == "bank_auth":
      current_page = handle_bank_auth(select_bank, total)

    if current_page == "ewallet":
      current_page, wallet = handle_ewallet()
      if wallet:
        select_ewallet = wallet

    if current_page == "ewallet_trans":
      current_page = handle_ewallet_trans(select_ewallet, total)

    if current_page == "pay_card":
      current_page = handle_pay_card()

    if current_page == "payment_success":
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

    if current_page == "view_transaction":
      current_page = handle_view_transaction(trans_acc, user_transactions)