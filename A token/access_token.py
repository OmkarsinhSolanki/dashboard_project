from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


kite = KiteConnect(api_key=API_KEY)
data = kite.generate_session("Ozg0DmhRCY1AAEqcaaSaY1KpUFu4YSb5", api_secret=API_SECRET)
access_token = data["access_token"]

print("Access Token:", access_token)

# save and run. you will get new access token.

# after geting access token, update '.env' and data/settings.py
