# main_app.py (updated structure)
import os
from dotenv import load_dotenv
import streamlit as st
from stocks_filter import main as box6_main
from value_editor import main as value_editor_main


st.set_page_config(
    page_title="Stock Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
