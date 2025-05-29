import streamlit as st

def format_zone_display(zone_types, directions):
    display_parts = []
    for z, d in zip(zone_types, directions):
        if z not in ["D1", "D2", "W", "M"]:
            continue
        color = "green" if d == "demand" else "red"
        display_parts.append(f"<span style='color:{color}'>{z}</span>")
    return " + ".join(display_parts) if display_parts else "<span style='color:gray'>N</span>"

def get_daily_scores(zone_types, directions, strength, base):
    for z, d in zip(zone_types, directions):
        if z in ["D1", "D2"]:
            return strength, base, strength + base
    return "-", "-", "-"

def update_rr_check(stock, checkbox_key, list_name):
    new_state = st.session_state[checkbox_key]
    for idx, item in enumerate(st.session_state.confirmation_list[list_name]):
        if item["stock"] == stock:
            st.session_state.confirmation_list[list_name][idx]["rr_check"] = new_state
            break

def update_in_trade_check(stock, checkbox_key, list_name):
    new_state = st.session_state[checkbox_key]
    for idx, item in enumerate(st.session_state.top_picks[list_name]):
        if item["stock"] == stock:
            st.session_state.top_picks[list_name][idx]["in_trade"] = new_state
            break

def add_to_confirmation_list(stock, sub_tab_key):
    lst = st.session_state.confirmation_list[sub_tab_key]
    if stock not in [item["stock"] for item in lst]:
        lst.append({"stock": stock, "rr_check": False})
        st.success(f"Added {stock} to Confirmation List {sub_tab_key.upper()}")
