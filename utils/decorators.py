import streamlit as st

def handle_data_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"Data error: {str(e)}")
            # Optionally return mock data or empty result
            return {}
    return wrapper
