import streamlit as st
from utils.helpers import format_zone_display, get_daily_scores, add_to_confirmation_list
from livedata.data_loader import DataLoader

data_loader = DataLoader()

# Load data
MANUAL_SECTOR_ORDER = data_loader.load_sectors()
MANUAL_STOCK_MAP = data_loader.load_stock_map()

all_symbols = list(MANUAL_STOCK_MAP.keys())
for sector_stocks in MANUAL_STOCK_MAP.values():
    all_symbols.extend(sector_stocks)
stock_data = data_loader.get_bulk_data(all_symbols)

def get_stocks_by_zone(MANUAL_STOCK_MAP, stock_data, tab_type, direction="supply"):
    from utils.zone_management import get_zones_with_scores

    tab_requirements = {
        "Daily-Daily": {"sector_zones": ["D1", "D2"], "stock_zones": ["D1", "D2"]},
        "Weekly-Daily": {"sector_zones": ["W"], "stock_zones": ["D1", "D2"]},
        "Weekly-Weekly": {"sector_zones": ["W"], "stock_zones": ["W"]},
        "Monthly-Monthly": {"sector_zones": ["M"], "stock_zones": ["M"]}
    }
    req = tab_requirements[tab_type]

    result = {}
    for sector, stocks in MANUAL_STOCK_MAP.items():
        # Get sector zones and filter
        sector_zones = [z for z in get_zones_with_scores(sector, is_sector=True) 
                      if (z['direction'] == direction and 
                          z['type'] in req["sector_zones"] and
                          # Add price check here
                          z['price_low'] <= stock_data.get(sector, {}).get('price', 0) <= z['price_high'])]
        
        if not sector_zones:
            continue

        # Aggregate sector data (combine all matching zones)
        sector_zone_types = "/".join({z['type'] for z in sector_zones})
        sector_strength = sum(z['strength'] for z in sector_zones)
        sector_base = sum(z['base'] for z in sector_zones)
        sector_total = sector_strength + sector_base

        # Filter and score stocks
        matched_stocks = []
        for stock in stocks:
            stock_zones = [z for z in get_zones_with_scores(stock, is_sector=False) 
                         if (z['direction'] == direction and 
                             z['type'] in req["stock_zones"] and
                             # Add price check here
                             z['price_low'] <= stock_data.get(stock, {}).get('price', 0) <= z['price_high'])]
            
            if stock_zones:
                stock_zone_types = "/".join({z['type'] for z in stock_zones})
                stock_strength = sum(z['strength'] for z in stock_zones)
                stock_base = sum(z['base'] for z in stock_zones)
                stock_total = stock_strength + stock_base
                matched_stocks.append({
                    'name': stock,
                    'zone_types': stock_zone_types,
                    'strength': stock_strength,
                    'base': stock_base,
                    'total': stock_total,
                    'price': stock_data.get(stock, {}).get('price', 0),
                    'pct_change': stock_data.get(stock, {}).get('pct_change', 0)
                })

        if matched_stocks:
            # Sort stocks by total score (descending)
            matched_stocks.sort(key=lambda x: x['total'], reverse=True)
            result[sector] = {
                'zone_types': sector_zone_types,
                'strength': sector_strength,
                'base': sector_base,
                'total': sector_total,
                'price': stock_data.get(sector, {}).get('price', 0),
                'pct_change': stock_data.get(sector, {}).get('pct_change', 0),
                'stocks': matched_stocks
            }

    # Sort sectors by total score (descending)
    return dict(sorted(result.items(), key=lambda x: x[1]['total'], reverse=True))


def render_zone_tab(MANUAL_STOCK_MAP, stock_data, tab_type, direction="supply"):
    sectors_data = get_stocks_by_zone(MANUAL_STOCK_MAP, stock_data, tab_type, direction)
    
    # Column headers
    cols = st.columns([2.2, 1.3, 1.1, 1, 1, 1.2, 1])  # Removed the last column
    headers = ["Name", "Zone Type", "Strength", "Base", "Total", "Price", "Chart"] 

    for col, h in zip(cols, headers):
        col.markdown(f"<div style='margin-bottom: 10px;'><strong>{h}</strong></div>", unsafe_allow_html=True)

    # Sector rows
    for sector_idx, (sector, data) in enumerate(sectors_data.items()):
        row = st.columns([2.2, 1.3, 1.1, 1, 1, 1.2, 1])
        row[0].markdown(f"**{sector}**")
        row[1].markdown(data['zone_types'])
        row[2].markdown(str(data['strength']))
        row[3].markdown(str(data['base']))
        row[4].markdown(f"**{data['total']}**")
        row[5].markdown(f"₹{data['price']:,.2f}")
        
        # Chart button
        if row[6].button("📈", key=f"chart_{direction}_{tab_type}_{sector_idx}_{sector}"):
            st.session_state['current_chart'] = sector


        # Stock rows (in expander)
        with st.expander("", expanded=False):
            for stock_idx, stock in enumerate(data['stocks']):
                s_row = st.columns([2.2, 1.3, 1.1, 1, 1, 1.2, 1])
                s_row[0].markdown(f"→ {stock['name']}")
                s_row[1].markdown(stock['zone_types'])
                s_row[2].markdown(str(stock['strength']))
                s_row[3].markdown(str(stock['base']))
                s_row[4].markdown(f"**{stock['total']}**")
                s_row[5].markdown(f"₹{stock['price']:,.2f}")
                
                if s_row[6].button("📈", key=f"chart_{direction}_{tab_type}_{sector_idx}_{stock_idx}_{stock['name']}"):
                    st.session_state['current_chart'] = stock['name']
                
