import streamlit as st
from dotenv import load_dotenv
import os

# Try reading from Streamlit secrets first
if st.secrets:
    API_KEY = st.secrets["kite"]["api_key"]
    API_SECRET = st.secrets["kite"]["api_secret"]
    ACCESS_TOKEN = st.secrets["kite"]["access_token"]
else:
    # Fallback to local .env file
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")