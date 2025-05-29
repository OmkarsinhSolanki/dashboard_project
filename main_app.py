import os
from dotenv import load_dotenv
import streamlit as st

# --------------------------
# 1. Page config MUST come first!
# --------------------------
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# 2. Then load credentials
# --------------------------
try:
    # Try Streamlit secrets (for deployment)
    API_KEY = st.secrets["kite"]["api_key"]
    API_SECRET = st.secrets["kite"]["api_secret"]
    ACCESS_TOKEN = st.secrets["kite"]["access_token"]
except:
    # Fallback to .env (for local dev)
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Validate credentials
if not all([API_KEY, API_SECRET, ACCESS_TOKEN]):
    st.error("⚠️ Missing Kite API credentials. Check secrets.toml or .env")
    st.stop() 

# After the credential-loading code in main_app.py
st.sidebar.write("Debug: Using secrets.toml?", "kite" in st.secrets)
st.sidebar.write("Debug: API_KEY loaded?", bool(API_KEY))

from stocks_filter import main as box6_main
from value_editor import main as value_editor_main


# streamlit run main_app.py


# Custom CSS to hide the default Streamlit menu and footer
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Stocks Analysis")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "✏️ Value Editor"],
    index=0
)

# Main app logic
if app_mode == "📊 Dashboard":
    box6_main()
else:
    value_editor_main()
