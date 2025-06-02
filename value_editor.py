import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from fuzzywuzzy import process
import git
from pathlib import Path
import json
import os



def save_and_push_to_github(data, file_name="zone_definitions.json"):
    try:
        repo_path = Path(__file__).parent.parent
        repo = git.Repo(repo_path)
        
        # Update the file
        file_path = repo_path / "data" / file_name
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        # Configure git
        repo.git.config("user.email", "your_email@example.com")
        repo.git.config("user.name", "Your GitHub Username")

        # Commit & Push with token authentication
        repo.git.add(file_path)
        repo.git.commit("-m", f"Auto-update {file_name}")
        
        # Get the GitHub token from secrets
        token = st.secrets.get("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN"))
        if not token:
            st.error("GitHub token not found in secrets!")
            return False
            
        origin = repo.remote(name="origin")
        origin_url = origin.url.replace(
            "https://github.com/",
            f"https://{token}@github.com/"
        )
        origin.set_url(origin_url)
        
        origin.push()
        return True
        
    except Exception as e:
        st.error(f"Error pushing to GitHub: {str(e)}")
        return False
        
# streamlit run value_editor.py

def load_zone_data():
    path = Path(__file__).parent / "data" / "zone_definitions.json"
    if not path.exists():
        return {"sectors": {}, "stocks": {}}
    with open(path) as f:
        return json.load(f)

def save_zone_data(data):
    path = Path(__file__).parent / "data" / "zone_definitions.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    if save_and_push_to_github(data, "zone_definitions.json"):
        st.success("Changes saved and pushed to GitHub!")
    else:
        st.warning("Changes saved locally but failed to push to GitHub")

def load_confirmation_data():
    path = Path(__file__).parent / "data" / "confirmation_list.json"
    if not path.exists():
        return {
            "demand_d2": [],
            "demand_d1": [],
            "supply_d2": [],
            "supply_d1": []
        }
    with open(path) as f:
        return json.load(f)

def save_confirmation_data(data):
    path = Path(__file__).parent / "data" / "confirmation_list.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    if save_and_push_to_github(data, "confirmation_list.json"):
        st.success("Changes saved and pushed to GitHub!")
    else:
        st.warning("Changes saved locally but failed to push to GitHub")

def load_stock_map():
    path = Path(__file__).parent / "data" / "stock_map.json"
    with open(path) as f:
        return json.load(f)

def load_sectors():
    path = Path(__file__).parent / "data" / "sectors.json"
    with open(path) as f:
        return list(json.load(f).keys())

def get_all_stocks():
    stock_map = load_stock_map()
    all_stocks = []
    for sector_stocks in stock_map.values():
        all_stocks.extend(sector_stocks)
    return sorted(list(set(all_stocks))) 

def fuzzy_search(query, choices, limit=5):
    """Fuzzy search with autocomplete"""
    if not query:
        return []
    results = process.extract(query, choices, limit=limit)
    return [result[0] for result in results]

def display_zone_form(zone_type, selected_item):
    zones_data = load_zone_data()
    key = 'sectors' if zone_type == 'sector' else 'stocks'
        
    with st.form(f"{zone_type}_zone_form"):
        col1, col2 = st.columns(2)
        price_low = col1.number_input("Price Low", value=0, step=1, key=f"{zone_type}_low")
        price_high = col2.number_input("Price High", value=0, step=1, key=f"{zone_type}_high")
        
        direction = st.selectbox("Direction", ["demand", "supply"], key=f"{zone_type}_dir")
        z_type = st.selectbox("Zone Type", ["D1", "D2", "W", "M"], key=f"{zone_type}_type")
        
        col3, col4 = st.columns(2)
        strength = col3.number_input("Strength", min_value=0, max_value=10, value=0, key=f"{zone_type}_str")
        base = col4.number_input("Base", min_value=0, max_value=10, value=0, key=f"{zone_type}_base")
        
        if st.form_submit_button("Add Zone"):
            new_zone = {
                "price_low": price_low,
                "price_high": price_high,
                "direction": direction,
                "type": z_type,
                "strength": strength,
                "base": base,
                "timestamp": datetime.now().isoformat()
            }
            
            if selected_item not in zones_data[key]:
                zones_data[key][selected_item] = []
            
            zones_data[key][selected_item].append(new_zone)
            save_zone_data(zones_data)
            st.success(f"{zone_type.capitalize()} zone added successfully!")
            st.rerun()

    existing_zones = zones_data[key].get(selected_item, [])
    if existing_zones:
        for i, zone in enumerate(existing_zones):
            with st.expander(f"Zone {i+1}: {zone['type']}"):
                st.json(zone)
                if st.button(f"Delete Zone {i+1}", key=f"del_{zone_type}_{selected_item}_{i}"):
                    zones_data[key][selected_item].pop(i)
                    save_zone_data(zones_data)
                    st.rerun()

def get_stock_zone_info(stock):
    """Get zone type and daily zone total score for a stock"""
    zones_data = load_zone_data()
    stock_zones = zones_data.get('stocks', {}).get(stock, [])
    
    if not stock_zones:
        return "", 0
    
    daily_zones = [z for z in stock_zones if z['type'] in ['D1', 'D2']]
    
    if not daily_zones:
        return "", 0
    
    zone_types = [z['type'] for z in daily_zones]
    
    total_score = sum(z['strength'] + z['base'] for z in daily_zones)
    
    zone_display = " + ".join(zone_types)
    
    return zone_display, total_score

def display_confirmation_form(selected_stock):
    confirmation_data = load_confirmation_data()
    
    with st.form(f"confirmation_form_{selected_stock}"):
  
        list_options = ["Demand D2", "Demand D1", "Supply D2", "Supply D1"]
        selected_list = st.selectbox("Confirmation List", list_options)
        

        zone_display, zone_total = get_stock_zone_info(selected_stock)
        

        st.markdown(f"**Zone Info:** {zone_display}, Total: {zone_total}")
        

        col1, col2, col3, col4 = st.columns(4)
        rsi_score = col1.number_input("RSI Score", min_value=0, max_value=10, value=0, step=1)
        sr_score = col2.number_input("S&R Score", min_value=0, max_value=10, value=0, step=1)
        fib_score = col3.number_input("Fib Score", min_value=0, max_value=10, value=0, step=1)
        rr_value = col4.number_input("RR Value", min_value=0.0, max_value=10.0, value=0.0, step=0.1, format="%.1f")
        
        if st.form_submit_button("Add to Confirmation List"):
            list_key = selected_list.lower().replace(" ", "_")
            
         
            new_entry = {
                "stock": selected_stock,
                "zone_display": zone_display,
                "zone_total": zone_total,
                "rsi": rsi_score,
                "sr": sr_score,
                "fib": fib_score,
                "rr": rr_value,
                "timestamp": datetime.now().isoformat()
            }
            

            confirmation_data[list_key].append(new_entry)
            save_confirmation_data(confirmation_data)
            st.success(f"Added {selected_stock} to {selected_list} confirmation list!")
            st.rerun()
    

    found_entries = False
    
    for list_name, entries in confirmation_data.items():
        stock_entries = [e for e in entries if e["stock"] == selected_stock]
        
        if stock_entries:
            found_entries = True
            for i, entry in enumerate(stock_entries):
                with st.expander(f"{list_name.replace('_', ' ').title()} Entry #{i+1}", expanded=False):
           
                    zone_disp = entry.get('zone_display', 'N/A')
                    zone_tot = entry.get('zone_total', 0)
                    rsi = entry.get('rsi', 0)
                    sr = entry.get('sr', 0)
                    fib = entry.get('fib', 0)
                    rr = entry.get('rr', 0.0)
                    final_score = zone_tot + rsi + sr + fib
                    
                    st.markdown(f"""
                    Stock: {entry['stock']}  
                    Zone: {zone_disp}  
                    Total: {zone_tot}  
                    RSI: {rsi}  
                    S&R: {sr}  
                    Fib: {fib}  
                    RR: {rr:.1f}  
                    Final Score: {final_score}
                    """)
                    
                    if st.button(f"Delete This Entry", key=f"del_conf_{entry['stock']}_{list_name}_{entry['timestamp']}"):
                        confirmation_data[list_name] = [e for e in entries if e != entry]
                        save_confirmation_data(confirmation_data)
                        st.rerun()
    
    if not found_entries:
        st.info("No confirmation entries found for this stock")

def load_top_picks_data():
    path = Path(__file__).parent / "data" / "top_picks.json"
    if not path.exists():
        return {
            "demand_d2": [],
            "demand_d1": [],
            "supply_d2": [],
            "supply_d1": []
        }
    with open(path) as f:
        return json.load(f)

def save_top_picks_data(data):
    path = Path(__file__).parent / "data" / "top_picks.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    if save_and_push_to_github(data, "top_picks.json"):
        st.success("Changes saved and pushed to GitHub!")
    else:
        st.warning("Changes saved locally but failed to push to GitHub")


def display_top_picks_form(selected_stock):
    top_picks_data = load_top_picks_data()
    confirmation_data = load_confirmation_data()

    with st.form(f"top_picks_form_{selected_stock}"):
       
        zone_display, zone_total = get_stock_zone_info(selected_stock)
        
    
        rr_score = 0.0
        final_score = zone_total
        has_confirmation_entry = False
        

        for list_name, entries in confirmation_data.items():
            for entry in entries:
                if entry["stock"] == selected_stock:
                    has_confirmation_entry = True
                    rr_score = max(rr_score, entry.get("rr", 0.0))
                    rsi = entry.get("rsi", 0)
                    sr = entry.get("sr", 0)
                    fib = entry.get("fib", 0)
                    final_score = max(final_score, zone_total + rsi + sr + fib)
                    break
            if has_confirmation_entry:
                break
        
   
        cols = st.columns([1.5, 1, 1.5, 1.5, 1])
        with cols[0]:
            st.markdown("Stock Info:")
        with cols[1]:
            st.markdown(zone_display)
        with cols[2]:
            st.markdown(f"Total: {zone_total}")
        with cols[3]:
            st.markdown(f"Final: {final_score}")
        with cols[4]:
            st.markdown(f"{rr_score:.1f}")      
        

        list_options = ["Demand D2", "Demand D1", "Supply D2", "Supply D1"]
        selected_list = st.selectbox("Top Picks List", list_options)
        
        # In Trade and Double Conf selection
        col1, col2 = st.columns(2)
        double_conf = col1.radio("Double Confirmation", ["yes", "No"], horizontal=True)
        in_trade = col2.radio("In Trade", ["✅", "No"], horizontal=True)
        
        if st.form_submit_button("Add to Top Picks"):
            if not has_confirmation_entry:
                st.warning("⚠️ This stock must first be added to the Confirmation List before it can be added to Top Picks.")
            else:
                list_key = selected_list.lower().replace(" ", "_")
                
                # Create new entry
                new_entry = {
                    "stock": selected_stock,
                    "zone_display": zone_display,
                    "zone_total": zone_total,
                    "final_score": final_score,
                    "rr_score": rr_score,
                    "in_trade": in_trade,
                    "double_conf": double_conf,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to top picks list
                top_picks_data[list_key].append(new_entry)
                save_top_picks_data(top_picks_data)
                st.success(f"✅ Added {selected_stock} to {selected_list} top picks!")
                st.rerun()
    
    # Display existing top picks entries for this stock
    found_entries = False
    
    for list_name, entries in top_picks_data.items():
        stock_entries = [e for e in entries if e["stock"] == selected_stock]
        
        if stock_entries:
            found_entries = True
            for i, entry in enumerate(stock_entries):
                with st.expander(f"{list_name.replace('_', ' ').title()} Entry #{i+1}", expanded=False):
                    st.markdown(f"""
                    **Stock:** {entry['stock']}  
                    **Zone:** {entry.get('zone_display', 'N/A')}  
                    **Total:** {entry.get('zone_total', 0)}  
                    **Final Score:** {entry.get('final_score', 0)}  
                    **Double Confirmation:** {entry.get('double_conf', 'No')}  
                    **In Trade:** {entry.get('in_trade', 'No')}
                    """)
                    
                    if st.button(f"Delete This Entry", key=f"del_top_{entry['stock']}_{list_name}_{entry['timestamp']}"):
                        top_picks_data[list_name] = [e for e in entries if e != entry]
                        save_top_picks_data(top_picks_data)
                        st.rerun()
    
    if not found_entries:
        st.info("No top picks entries found for this stock")

def main():
    st.subheader("Stocks Value Editor")
    
    all_sectors = load_sectors()
    all_stocks = get_all_stocks()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Sectors", "Stocks", "Confirmation List", "Top Picks"])    
   
    with tab1:
        sector_query = st.text_input("Search Sector", key="sector_search", 
                                   placeholder="Start typing to search sectors...")
        
        if sector_query:
            matched_sectors = fuzzy_search(sector_query, all_sectors)
            
            if not matched_sectors:
                st.warning("No matching sectors found")
            else:
                selected_sector = matched_sectors[0]
                display_zone_form('sector', selected_sector)
        else:
            st.info("Enter a sector name to begin")
    
    with tab2:
        stock_query = st.text_input("Search Stock", key="stock_search",
                                  placeholder="Start typing to search stocks...")
        
        if stock_query:
            matched_stocks = fuzzy_search(stock_query, all_stocks)
            
            if not matched_stocks:
                st.warning("No matching stocks found")
            else:
                selected_stock = matched_stocks[0]
                display_zone_form('stock', selected_stock)
        else:
            st.info("Enter a stock name to begin")
            
    with tab3:
        conf_stock_query = st.text_input("Search Stock for Confirmation", key="conf_stock_search",
                                       placeholder="Start typing to search stocks...")
        
        if conf_stock_query:
            matched_stocks = fuzzy_search(conf_stock_query, all_stocks)
            
            if not matched_stocks:
                st.warning("No matching stocks found")
            else:
                selected_stock = matched_stocks[0]
                display_confirmation_form(selected_stock)
        else:
            st.info("Enter a stock name to manage confirmation list entries")

    with tab4:
        top_picks_query = st.text_input("Search Stock for Top Picks", key="top_picks_search",
                                      placeholder="Start typing to search stocks...")
        
        if top_picks_query:
            matched_stocks = fuzzy_search(top_picks_query, all_stocks)
            
            if not matched_stocks:
                st.warning("No matching stocks found")
            else:
                selected_stock = matched_stocks[0]
                display_top_picks_form(selected_stock)
        else:
            st.info("Enter a stock name to manage top picks entries")

if __name__ == "__main__":
    st.set_page_config(page_title="Value Editor", layout="wide")
    main()
