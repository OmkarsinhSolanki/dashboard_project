import os
from dotenv import load_dotenv
import streamlit as st


try:
    # Try reading from Streamlit secrets first
    API_KEY = st.secrets["kite"]["api_key"]
    API_SECRET = st.secrets["kite"]["api_secret"]
    ACCESS_TOKEN = st.secrets["kite"]["access_token"]
except:
    # Fallback to local .env file
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    
    # If still not found, use empty strings (app will show error)
    if not API_KEY:
        API_KEY = ""
    if not API_SECRET:
        API_SECRET = ""
    if not ACCESS_TOKEN:
        ACCESS_TOKEN = ""

# Add validation
if not all([API_KEY, API_SECRET, ACCESS_TOKEN]):
    st.error("⚠️ Missing Kite API credentials. Please check your configuration.")
    # st.stop() if st.running() else None

USE_LIVE_DATA = True
