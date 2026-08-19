from features import load_reserve, dump_reserve
from helpers.selection_helper import search, select
from helpers.cli_helper import clear
from config import attraction_data

def reserve_attraction(user_id):
    clear()
    user_data = load_reserve()
    current_page = ""


