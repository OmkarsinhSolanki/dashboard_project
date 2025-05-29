from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
# do every time
# https://kite.trade/connect/login?api_key=sga0oscku88h6hhi&v=3
# use the link ginen above to get new 'request token" and ureplace it with your_request_token down here.

kite = KiteConnect(api_key="sga0oscku88h6hhi")
data = kite.generate_session("Ozg0DmhRCY1AAEqcaaSaY1KpUFu4YSb5", api_secret="3sxovyrdcawudyy33f6yjom964x759tw")
access_token = data["access_token"]

print("Access Token:", access_token)

# save and run. you will get new access token.

# after geting access token, update '.env' and data/settings.py
