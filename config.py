#module name  : config.py
#date created : 11th August 2026
#created by   : 
#imported     : pathlib, pandas, os
#amendment    :
#remark       : Configuration

from pathlib import Path
import pandas as pd
import os

BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)
(BASE_DIR / "saves").mkdir(parents=True, exist_ok=True)

LOGIN_PATH = BASE_DIR / "saves" / "login.json"
RESERVES_PATH = BASE_DIR / "saves" / "reserves.json"
ROOM_AVAILABILITY_PATH = BASE_DIR / "saves" / "room_availability.json"
TRANSACTION_PATH = BASE_DIR / "saves" / "transaction_history.json"
DATA_FOLDER = BASE_DIR / "data"

hotel_data = pd.read_csv(DATA_FOLDER / "malaysia_hotels.csv")
car_data = pd.read_csv(DATA_FOLDER /"car_models.csv")
attraction_data = pd.read_csv(DATA_FOLDER / "malaysia_attractions.csv")

# pd.read_csv reads the .csv file and outputs a DataFrame