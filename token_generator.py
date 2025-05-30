import streamlit as st
from kiteconnect import KiteConnect
from pathlib import Path
import webbrowser
import urllib.parse

# Configure page
st.set_page_config(
    page_title="Kite Connect Token Generator",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("Kite Connect Token Generator")

def main():
    # Step 1: Show API Key and Login Button
    st.subheader("Step 1: Login to Kite Connect")
    
    if 'api_key' not in st.session_state:
        try:
            st.session_state.api_key = st.secrets["kite"]["api_key"]
            st.session_state.api_secret = st.secrets["kite"]["api_secret"]
        except:
            st.error("API credentials not found in secrets.toml")
            return
    
    st.write(f"API Key: `{st.session_state.api_key}`")
    
    if st.button("Login to Kite Connect"):
        login_url = f"https://kite.trade/connect/login?api_key={st.session_state.api_key}&v=3"
        st.markdown(f"[Click here if not redirected automatically]({login_url})")
        webbrowser.open_new_tab(login_url)
    
    # Step 2: Get Request Token
    st.subheader("Step 2: Enter Request Token")
    st.markdown("""
    1. After logging in, you'll be redirected to your redirect URL
    2. Copy the `request_token` from the URL (looks like `?request_token=AbC123...`)
    """)
    
    request_token = st.text_input("Paste Request Token Here", key="request_token")
    
    # Step 3: Generate and Save Token
    if st.button("Generate Access Token"):
        if not request_token:
            st.error("Please enter the request token")
            return
            
        try:
            kite = KiteConnect(api_key=st.session_state.api_key)
            data = kite.generate_session(request_token, api_secret=st.session_state.api_secret)
            access_token = data["access_token"]
            
            st.success("Access Token Generated Successfully!")
            st.subheader("Your Access Token:")
            st.code(access_token)
            
            # Step 4: Save Configuration
            st.subheader("Step 3: Save Configuration")
            
            # Option 1: Show instructions for Streamlit Cloud
            st.markdown("""
            **For Streamlit Cloud:**
            1. Go to [Streamlit Share Settings](https://share.streamlit.io/)
            2. Select your app
            3. Go to Settings → Secrets
            4. Update the access_token value:
            ```toml
            [kite]
            api_key = "{st.session_state.api_key}"
            api_secret = "{st.session_state.api_secret}"
            access_token = "{access_token}"
            ```
            """)
            
            # Option 2: Save to .env file locally
            if st.checkbox("Save to .env file (for local development)"):
                env_path = Path(__file__).parent / "venv/.env"
                env_path.parent.mkdir(exist_ok=True)
                
                with open(env_path, "w") as f:
                    f.write(f"""API_KEY={st.session_state.api_key}
API_SECRET={st.session_state.api_secret}
ACCESS_TOKEN={access_token}
USE_LIVE_DATA=True
""")
                st.success("Saved to .env file!")
                
        except Exception as e:
            st.error(f"Error generating token: {str(e)}")

if __name__ == "__main__":
    main()
