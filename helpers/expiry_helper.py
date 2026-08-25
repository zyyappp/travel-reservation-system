#module name  : expiry_helper.py
#date created : 25th August 2026
#created by   : 
#imported     : datetime
#amendment    :
#remark       : Check whether a reservation expired
from datetime import datetime


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