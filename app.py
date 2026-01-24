import streamlit as st
import requests
import pandas as pd
import time

# ==========================================
# 1. CONFIGURATION & SECRETS
# ==========================================
# We fetch these safely from the hosting platform's secret vault
try:
    ACCOUNT_ID = st.secrets["ACCOUNT_ID"]
    API_TOKEN = st.secrets["API_TOKEN"]
    ENVIRONMENT = st.secrets["ENVIRONMENT"] # "live" or "practice"
except FileNotFoundError:
    st.error("Secrets not found! Please configure them in your hosting dashboard.")
    st.stop()

# ==========================================
# 2. UI SETUP (Dark Theme)
# ==========================================
st.set_page_config(page_title="COMMAND INTERFACE", layout="centered")

# Custom CSS to mimic your "Glass/Dark" look
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #808e9b; }
    .metric-card {
        background-color: #1e272e;
        border: 1px solid #485460;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .big-font { font-size: 40px; color: #0be881; font-weight: bold; font-family: monospace; }
    .header-font { font-size: 14px; color: #808e9b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DATA ENGINE
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
# 4. MAIN INTERFACE
# ==========================================
st.markdown("### NAV MONITOR")

# Placeholder for auto-updating data
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
                # Profit Logic (Reused from your code)
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
                        # Secure Profit Check
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
