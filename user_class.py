import subprocess
from config import DATA_FOLDER, BASE_DIR
from helpers.selection_helper import search
import pandas as pd
from features.reservation import select_city

class User:
    def __init__(self, id, user, password):
        self.id = id
        self.user = user
        self.password = password
        self.city = select_city(id)

###
# reserves.json: 
# 
# [
# {
# "user" : username,
# "city" : city,
# ...
# }]###