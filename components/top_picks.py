import streamlit as st
from utils.helpers import format_zone_display
from utils.zone_management import get_zones_with_scores  # Add this import
from livedata.data_loader import DataLoader

data_loader = DataLoader()

# Load data
MANUAL_SECTOR_ORDER = data_loader.load_sectors()
MANUAL_STOCK_MAP = data_loader.load_stock_map()

all_symbols = list(MANUAL_STOCK_MAP.keys())
for sector_stocks in MANUAL_STOCK_MAP.values():
    all_symbols.extend(sector_stocks)
stock_data = data_loader.get_bulk_data(all_symbols)

# Constants
confirmation_subtabs = ["Demand D2", "Demand D1", "Supply D2", "Supply D1"]

def get_stock_zone_info(stock):
    """Get zone type and daily zone total score for a stock"""
    zones_data = get_zones_with_scores(stock, is_sector=False)
    
    if not zones_data:
        return "", 0
    
    # Filter for daily zones only (D1, D2)
    daily_zones = [z for z in zones_data if z['type'] in ['D1', 'D2']]
    
    if not daily_zones:
        return "", 0
    
    # Get zone types (without direction)
    zone_types = [z['type'] for z in daily_zones]
    
    # Calculate total score from daily zones only
    total_score = sum(z['strength'] + z['base'] for z in daily_zones)
    
    # Format zone display without direction indicators
    zone_display = " + ".join(zone_types)
    
    return zone_display, total_score


def render_top_picks(stock_data):
    from livedata.live_market_data_services import LiveMarketDataService
    data_service = LiveMarketDataService()
    
    visible_symbols = set()

    st.markdown("")
    subtabs = st.tabs(confirmation_subtabs)
    
    for subtab_idx, subtab in enumerate(subtabs):
        with subtab:
            list_name = confirmation_subtabs[subtab_idx].lower().replace(" ", "_")
            stocks = st.session_state.top_picks.get(list_name, [])
            
            # Column headers
            cols = st.columns([2, 1.2, 1, 1, 1.2, 1, 1, 1])
            headers = ["Stock", "Zone Type", "Total", "Final", "double conf", "In Trade", "Price", "Chart"]
            for col, h in zip(cols, headers):
                col.markdown(f"<div style='margin-bottom: 30px;'><large><strong>{h}</strong></large></div>", unsafe_allow_html=True)
            
            # Sort by final score descending
            sorted_stocks = sorted(
                stocks,
                key=lambda s: (
                    stock_data.get(s["stock"], {}).get("strength", 0) + 
                    stock_data.get(s["stock"], {}).get("base", 0) +
                    st.session_state.score_data.get(s["stock"], {}).get('rsi', 0) +
                    st.session_state.score_data.get(s["stock"], {}).get('sr', 0) +
                    st.session_state.score_data.get(s["stock"], {}).get('fib', 0)
                ),
                reverse=True
            )
            
            for stock_idx, stock_item in enumerate(sorted_stocks):
                stock = stock_item["stock"]
                visible_symbols.add(stock)
                data = stock_data.get(stock, {})
                
                zone_display, zone_total = get_stock_zone_info(stock)
                final_score = stock_item.get('final_score', 0)
                double_conf = stock_item.get('double_conf', 'No')
                in_trade = stock_item.get('in_trade', 'No')
                price = data.get('price', 0)
                
                
                # Create row
                row = st.columns([2, 1.2, 1, 1, 1.2, 1, 1, 1])
                row[0].markdown(f"<span style='color:white'>{stock}</span>", unsafe_allow_html=True)
                row[1].markdown(zone_display, unsafe_allow_html=True)
                row[2].markdown(str(zone_total))
                row[3].markdown(f"**{final_score}**")
                row[4].markdown(double_conf)
                row[5].markdown(in_trade)
                row[6].markdown(f"₹{price:,.2f}")
                
                # Chart button
                if row[7].button("📈", key=f"top_pick_chart_{stock}_{list_name}_{stock_idx}"):
                    st.session_state['current_chart'] = stock
                    st.toast(f"Loading {stock} chart in Box 4...")

    data_service.set_priority_symbols(list(visible_symbols))