import streamlit as st
import requests
import pandas as pd
import time

# ==========================================
# 1. CONFIGURATION & SECRETS
# ==========================================
try:
    if "ACCOUNT_ID" in st.secrets:
        ACCOUNT_ID = st.secrets["ACCOUNT_ID"]
        API_TOKEN = st.secrets["API_TOKEN"]
        ENVIRONMENT = st.secrets["ENVIRONMENT"]
    else:
        # Fallback for local testing if secrets aren't set
        ACCOUNT_ID = "000-000-0000000-000"
        API_TOKEN = "token"
        ENVIRONMENT = "practice"
except:
    st.stop()

# ==========================================
# 2. UI SETUP & STATE MANAGEMENT
# ==========================================
st.set_page_config(page_title="COMMAND INTERFACE", layout="centered")

# Initialize Session State for the Secure Toggle
if 'secure_mode' not in st.session_state:
    st.session_state.secure_mode = False # Starts transparent

def toggle_secure():
    st.session_state.secure_mode = not st.session_state.secure_mode

# Determine Background Color based on State
# If secure: Black. If not secure: Transparent.
overlay_color = "#000000" if st.session_state.secure_mode else "rgba(0,0,0,0)"

# ==========================================
# 3. THE OVERLAY BUTTON (Cover Everything)
# ==========================================
# We create a button with an empty label. 
# We place it BEFORE the main loop so it renders first.
st.button(" ", on_click=toggle_secure, key="overlay_btn")

# CSS to force the button to cover the entire screen
st.markdown(f"""
    <style>
    /* GLOBAL DARK THEME */
    .stApp {{ background-color: #000000; color: #808e9b; }}

    /* OVERLAY BUTTON STYLING */
    div.stButton > button {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 999999 !important; /* Sit on top of everything */
        
        /* Dynamic Color: Black or Transparent */
        background-color: {overlay_color} !important;
        
        border: none !important;
        color: transparent !important; /* Hide text */
        cursor: pointer;
        transition: background-color 0.3s ease; /* Smooth fade effect */
    }}
    
    /* Remove hover effects to keep it invisible/flat */
    div.stButton > button:hover {{
        background-color: {overlay_color} !important;
        border: none !important;
    }}
    div.stButton > button:active {{
        background-color: {overlay_color} !important;
        border: none !important;
    }}

    /* METRIC CARD STYLING */
    .metric-card {{
        background-color: #1e272e;
        border: 1px solid #485460;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }}
    .big-font {{ font-size: 40px; color: #0be881; font-weight: bold; font-family: monospace; }}
    .header-font {{ font-size: 14px; color: #808e9b; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DATA ENGINE
# ==========================================
def get_data():
    base_url = "https://api-fxtrade.oanda.com/v3/accounts" if ENVIRONMENT == "live" else "https://api-fxpractice.oanda.com/v3/accounts"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    try:
        r1 = requests.get(f"{base_url}/{ACCOUNT_ID}/summary", headers=headers, timeout=5)
        r2 = requests.get(f"{base_url}/{ACCOUNT_ID}/openTrades", headers=headers, timeout=5)
        
        if r1.status_code == 200 and r2.status_code == 200:
            return r1.json()['account'], r2.json()['trades']
        else:
            return None, None
    except Exception as e:
        return None, None

# ==========================================
# 5. MAIN INTERFACE
# ==========================================
# Only render the UI content (behind the button)
st.markdown("### NAV MONITOR")

placeholder = st.empty()

while True:
    acct, trades = get_data()
    
    with placeholder.container():
        # --- TOP MODULE: NAV ---
        if acct:
            nav = float(acct['NAV'])
            st.markdown(f"""
                <div class="metric-card">
                    <div class="header-font">NET ASSET VALUE</div>
                    <div class="big-font">£{nav:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Connecting...")

        # --- BOTTOM MODULE: TRADES ---
        st.markdown("### ACTIVE TRANSMISSIONS")
        
        if trades:
            trade_data = []
            for t in trades:
                entry = float(t.get('price', 0))
                units = float(t['currentUnits'])
                current_pl = float(t['unrealizedPL'])
                
                # TSL Calculation
                tsl_status = "Wait"
                tsl_val = "-"
                
                if 'trailingStopLossOrder' in t:
                    tsl_trigger = t['trailingStopLossOrder'].get('triggerPrice')
                    if tsl_trigger:
                        trigger_price = float(tsl_trigger)
                        tsl_val = f"{trigger_price:.3f}"
                        if units > 0 and trigger_price > entry: tsl_status = "LOCKED"
                        elif units < 0 and trigger_price < entry: tsl_status = "LOCKED"

                trade_data.append({
                    "DIR": "LONG" if units > 0 else "SHORT",
                    "INST": t['instrument'],
                    "P/L": f"£{current_pl:.2f}",
                    "TSL": tsl_val,
                    "PROFIT": tsl_status
                })
            
            df = pd.DataFrame(trade_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No Active Transmissions")

    # Refresh every 2 seconds
    time.sleep(2)
