import streamlit as st
from kiteconnect import KiteConnect
from data.settings import API_KEY, ACCESS_TOKEN


# streamlit run main_app.py

def verify_access_token():
    """Test the access token by fetching data for a real stock (e.g., 'RELIANCE')."""
    try:
        kite = KiteConnect(api_key=API_KEY)
        kite.set_access_token(ACCESS_TOKEN)
        
        # Try to fetch data for a reliable stock (e.g., RELIANCE)
        test_data = kite.ltp(["NSE:RELIANCE"])
        
        if not test_data or "NSE:RELIANCE" not in test_data:
            raise Exception("No data received for the test stock.")
        return True
    except Exception as e:
        st.error(f"❌ ACCESS TOKEN VERIFICATION FAILED: {str(e)}")
        st.error("**The app cannot proceed.** Possible reasons:")
        st.error("1. Access token is invalid/expired.")
        st.error("2. API key is incorrect.")
        st.error("3. Network issues (check internet connection).")
        st.error("\n**Solution:** Update the access token in `.streamlit/secrets.toml` or `.env` and restart the app.")
        return False

if not verify_access_token():
    st.stop()  # Hard stop - nothing below this runs if verification fails.

st.set_page_config(
    page_title="Stock Analysis Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

from stocks_filter import main as box6_main
from value_editor import main as value_editor_main

# Hide default Streamlit UI
hide_st_style = """
    <style> #MainMenu, footer, header { visibility: hidden; } </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Main App Navigation
st.sidebar.title("Stocks Analysis")
st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "✏️ Value Editor"],
    index=0
)

if app_mode == "📊 Dashboard":
    box6_main()
else:
    value_editor_main()
