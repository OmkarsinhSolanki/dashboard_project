import os
from dotenv import load_dotenv
import streamlit as st

def get_credential(key):
    """Try multiple sources for credentials with clear error messaging"""
    try:
        # 1. First try Streamlit secrets
        if st.secrets.has_key("kite"):
            return st.secrets["kite"][key]
    except:
        pass
    
    try:
        # 2. Try environment variables (for local development)
        load_dotenv()
        return os.getenv(key.upper())
    except:
        pass
    
    # 3. Final fallback - return empty string
    return ""

API_KEY = get_credential("api_key") or ""
API_SECRET = get_credential("api_secret") or ""
ACCESS_TOKEN = get_credential("access_token") or ""

# Add validation
if not all([API_KEY, API_SECRET, ACCESS_TOKEN]):
    st.error("⚠️ Missing Kite API credentials. Please check your configuration.")
    st.stop() if st.running() else None

USE_LIVE_DATA = True
