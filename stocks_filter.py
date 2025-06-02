import streamlit as st
from pathlib import Path
import json
import time
from datetime import datetime
from livedata.data_loader import DataLoader
from components.manual_list import render_manual_tab
from components.demand_zones import render_zone_tab as render_demand_zone_tab
from components.supply_zones import render_zone_tab as render_supply_zone_tab
from components.confirmation import render_confirmation_list
from components.top_picks import render_top_picks
from components.chart import render_chart

# streamlit run stocks_filter.py

def main():
    # Initialize session state variables FIRST
    if 'refresh_settings' not in st.session_state:
        st.session_state.refresh_settings = {
            'interval': 60,  # Default 1 minute
            'last_refresh': time.time(),
            'auto_refresh': True
        }

    # Refresh interval control - SIMPLIFIED AND RELIABLE
    current_interval = st.session_state.refresh_settings['interval']
    new_interval = st.number_input(
        "Refresh Interval (minutes)",
        min_value=1,
        max_value=60,
        value=current_interval,
        step=1,
        key='refresh_interval_input'
    )

    # Update session state if changed
    if new_interval != current_interval:
        st.session_state.refresh_settings['interval'] = new_interval
        st.session_state.refresh_settings['last_refresh'] = time.time()
        st.rerun()

    # Auto-refresh logic
    current_time = time.time()
    elapsed = current_time - st.session_state.refresh_settings['last_refresh']
    refresh_interval_seconds = st.session_state.refresh_settings['interval'] * 60

    if elapsed >= refresh_interval_seconds:
        st.session_state.refresh_settings['last_refresh'] = current_time
        st.rerun()

    # Meta refresh tag
    time_remaining = max(1, int(refresh_interval_seconds - elapsed))
    st.write(f'<meta http-equiv="refresh" content="{time_remaining}">', unsafe_allow_html=True)

    # Create DataLoader instance 
    data_loader = DataLoader()

    # Load data using the instance
    MANUAL_SECTOR_ORDER = data_loader.load_sectors()
    MANUAL_STOCK_MAP = data_loader.load_stock_map()

    all_symbols = list(MANUAL_STOCK_MAP.keys())
    for sector_stocks in MANUAL_STOCK_MAP.values():
        all_symbols.extend(sector_stocks)
    stock_data = data_loader.get_bulk_data(all_symbols)

    # Initialize other session state variables
    if "confirmation_list" not in st.session_state:
        try:
            path = Path(__file__).parent / "data" / "confirmation_list.json"
            with open(path) as f:
                st.session_state.confirmation_list = json.load(f)
        except:
            st.session_state.confirmation_list = {
                "demand_d2": [],
                "demand_d1": [],
                "supply_d2": [],
                "supply_d1": []
            }
            
    if "top_picks" not in st.session_state:
        try:
            path = Path(__file__).parent / "data" / "top_picks.json"
            with open(path) as f:
                st.session_state.top_picks = json.load(f)
        except:
            st.session_state.top_picks = {
                "demand_d2": [],
                "demand_d1": [],
                "supply_d2": [],
                "supply_d1": []
            }
                    
    if "score_edits" not in st.session_state:
        st.session_state.score_edits = {}

    if "score_data" not in st.session_state:
        st.session_state.score_data = {}

    # Constants
    sub_tab_labels = ["Daily-Daily", "Weekly-Daily", "Weekly-Weekly", "Monthly-Monthly"]
    confirmation_subtabs = ["Demand D2", "Demand D1", "Supply D2", "Supply D1"]

    # Main App Layout
    st.subheader("Stocks Filter")

    # Then: Render Tabs below the chart
    main_tabs = st.tabs([
        "Box 6A Manual List", 
        "Box 6B Demand Zones", 
        "Box 6C Supply Zones", 
        "Box 6D Confirmation List", 
        "Box 6E Top Picks"
    ])

    with main_tabs[0]:
        render_manual_tab()

    with main_tabs[1]:  # Demand Zones
        demand_sub_tabs = st.tabs(["Daily-Daily", "Weekly-Daily", "Weekly-Weekly", "Monthly-Monthly"])
        for i, label in enumerate(sub_tab_labels):
            with demand_sub_tabs[i]:
                render_demand_zone_tab(MANUAL_STOCK_MAP, stock_data, label, "demand")

    with main_tabs[2]:  # Supply Zones
        supply_sub_tabs = st.tabs(["Daily-Daily", "Weekly-Daily", "Weekly-Weekly", "Monthly-Monthly"])
        for i, label in enumerate(sub_tab_labels):
            with supply_sub_tabs[i]:
                render_supply_zone_tab(MANUAL_STOCK_MAP, stock_data, label, "supply")

    with main_tabs[3]:
        render_confirmation_list(stock_data)  

    with main_tabs[4]:
        render_top_picks(stock_data)

    st.title("")
    render_chart()

if __name__ == "__main__":
    st.set_page_config(page_title="Zone Dashboard", layout="wide")
    main()
