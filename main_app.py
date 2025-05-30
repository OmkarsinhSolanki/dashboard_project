import streamlit as st
from kiteconnect import KiteConnect
from data.settings import API_KEY, ACCESS_TOKEN
from token_generator import main as token_generator_main

# streamlit run main_app.py

st.set_page_config(
    page_title="Stock Analysis Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main App Navigation
st.sidebar.title("Stocks Analysis")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "✏️ Value Editor", "🔑 Token Generator"],
    index=0
)

if app_mode == "🔑 Token Generator":
    token_generator_main()


from stocks_filter import main as box6_main
from value_editor import main as value_editor_main

# Hide default Streamlit UI
hide_st_style = """
    <style> #MainMenu, footer, header { visibility: hidden; } </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)


if app_mode == "📊 Dashboard":
    box6_main()
else:
    value_editor_main()
