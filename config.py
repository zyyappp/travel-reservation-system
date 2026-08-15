from pathlib import Path
import pandas as pd
import os

BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)

LOGIN_PATH = BASE_DIR / "saves" / "login.json"
RESERVES_PATH = BASE_DIR / "saves" / "reserves.json"
DATA_FOLDER = BASE_DIR / "data"

hotel_data = pd.read_csv(DATA_FOLDER / "malaysia_hotels.csv")
car_data = pd.read_csv(DATA_FOLDER /"car_models.csv")