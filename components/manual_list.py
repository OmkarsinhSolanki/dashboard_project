import streamlit as st
from utils.helpers import format_zone_display
from livedata.data_loader import DataLoader
from utils.zone_management import get_active_zones  # Add this import

def render_manual_tab():
    # Initialize DataLoader
    data_loader = DataLoader()

    # Load data
    MANUAL_SECTOR_ORDER = data_loader.load_sectors()
    MANUAL_STOCK_MAP = data_loader.load_stock_map()

    try:
        all_symbols = list(MANUAL_STOCK_MAP.keys())
        for sector_stocks in MANUAL_STOCK_MAP.values():
            all_symbols.extend(sector_stocks)
        
        stock_data = data_loader.get_bulk_data(all_symbols)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        stock_data = {}

    # Initialize LiveMarketDataService for priority updates
    from livedata.live_market_data_services import LiveMarketDataService
    data_service = LiveMarketDataService()
    visible_symbols = set()

    # Render zone popup if activated
    if st.session_state.get('show_zone_popup', False):
        from utils.zone_management import add_zone_popup
        target = st.session_state['zone_edit_target']
        add_zone_popup(target['type'], target['name'])

    st.markdown("")
    cols = st.columns([2.2, 1.3, 1.1, 1, 1, 1.2, 1])  # Added extra column for Zone button
    headers = ["Name", "Zone Type", "Strength", "Base", "Total", "Price", "Chart"]
    
    for col, h in zip(cols, headers):
        col.markdown(f"<div style='margin-bottom: 30px;'><large><strong>{h}</strong></large></div>", unsafe_allow_html=True)

    for sector_idx, sector in enumerate(MANUAL_SECTOR_ORDER):
        sector_data = stock_data.get(sector, {})
        
        # Get active zones for sector
        price = sector_data.get("price", 0)
        active_zones = get_active_zones(sector, price, is_sector=True)
        zone_types = [zone['type'] for zone in active_zones]
        directions = [zone['direction'] for zone in active_zones]
        strength = sum(zone['strength'] for zone in active_zones) if active_zones else 0
        base = sum(zone['base'] for zone in active_zones) if active_zones else 0

        # Format display values
        price_display = f"₹{price:,.2f}" if price else "N/A"
        zone_display = format_zone_display(zone_types, directions) or "N/A"
        
        # Create row columns
        row = st.columns([2.2, 1.3, 1.1, 1, 1, 1.2, 1])
        
        # Display data
        row[0].markdown(f"<div style='margin-bottom: -10px;'><medium><strong>{sector}</strong></medium></div>", unsafe_allow_html=True)
        row[1].markdown(f"<div style='margin-bottom: -10px;'><medium>{zone_display}</medium></div>", unsafe_allow_html=True)
        row[2].markdown(f"<div style='margin-bottom: -10px;'><medium>{strength}</medium></div>", unsafe_allow_html=True)
        row[3].markdown(f"<div style='margin-bottom: -10px;'><medium>{base}</medium></div>", unsafe_allow_html=True)
        row[4].markdown(f"<div style='margin-bottom: -10px;'><medium>{strength + base}</medium></div>", unsafe_allow_html=True)
        row[5].markdown(f"<div style='margin-bottom: -10px;'><medium>{price_display}</medium></div>", unsafe_allow_html=True)
        
        if row[6].button("📈", key=f"manual_chart_sector_{sector}_{sector_idx}"):
            st.session_state['current_chart'] = sector
            st.rerun()
            
        with st.expander("", expanded=False):
            sorted_stocks = sorted(
                MANUAL_STOCK_MAP.get(sector, []),
                key=lambda s: (
                    stock_data.get(s, {}).get("strength", 0) + 
                    stock_data.get(s, {}).get("base", 0),
                ),
                reverse=True
            )
        
            for stock_idx, stock in enumerate(sorted_stocks):
                visible_symbols.add(stock)
                data = stock_data.get(stock, {})
                
                # Get active zones for stock
                price = data.get("price", 0)
                active_zones = get_active_zones(stock, price)
                zone_types = [zone['type'] for zone in active_zones]
                directions = [zone['direction'] for zone in active_zones]
                s_strength = sum(zone['strength'] for zone in active_zones) if active_zones else 0
                s_base = sum(zone['base'] for zone in active_zones) if active_zones else 0
                s_total = s_strength + s_base

                zone_display = format_zone_display(zone_types, directions)

                stock_row = st.columns([2.2, 1.3, 1.1, 1, 1, 1.2, 1])
                stock_row[0].markdown(f"<div style='margin-bottom: -10px;'><medium>{stock}</medium></div>", unsafe_allow_html=True)
                stock_row[1].markdown(f"<div style='margin-bottom: -10px;'><medium>{zone_display}</medium></div>", unsafe_allow_html=True)
                stock_row[2].markdown(f"<div style='margin-bottom: -10px;'><medium>{s_strength}</medium></div>", unsafe_allow_html=True)
                stock_row[3].markdown(f"<div style='margin-bottom: -10px;'><medium>{s_base}</medium></div>", unsafe_allow_html=True)
                stock_row[4].markdown(f"<div style='margin-bottom: -10px;'><medium>{s_total}</medium></div>", unsafe_allow_html=True)
                stock_row[5].markdown(f"<div style='margin-bottom: -10px;'><medium>₹{price:,.2f}</medium></div>", unsafe_allow_html=True)
                
                if stock_row[6].button("📈", key=f"manual_chart_stock_{sector}_{stock}_{stock_idx}"):
                    st.session_state['current_chart'] = stock
                    st.toast(f"Loading {stock} chart in Box 4...")
                    
    # Update priority symbols for live updates
    data_service.set_priority_symbols(list(visible_symbols))
