import subprocess
from config import DATA_FOLDER
from selection_helper import search
import pandas as pd
from reservation import select_city
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