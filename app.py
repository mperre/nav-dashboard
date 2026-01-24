import streamlit as st
import requests
import time

# ==========================================
# 1. CONFIGURATION & SECRETS
# ==========================================
st.set_page_config(page_title="COMMAND INTERFACE", layout="wide")

# Initialize State
if 'secure_mode' not in st.session_state:
    st.session_state.secure_mode = False

def toggle_secure():
    st.session_state.secure_mode = not st.session_state.secure_mode

# Fetch Secrets
try:
    if "ACCOUNT_ID" in st.secrets:
        ACCOUNT_ID = st.secrets["ACCOUNT_ID"]
        API_TOKEN = st.secrets["API_TOKEN"]
        ENVIRONMENT = st.secrets["ENVIRONMENT"]
    else:
        ACCOUNT_ID = "000-000-0000000-000"
        API_TOKEN = "token"
        ENVIRONMENT = "practice"
except:
    st.stop()

# ==========================================
# 2. CSS STYLING & OVERLAY LOGIC
# ==========================================
# Determine overlay color based on state
# False = Transparent (See dashboard). True = Black (Hide dashboard).
overlay_color = "#000000" if st.session_state.secure_mode else "rgba(0,0,0,0)"

css_template = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* GLOBAL RESET */
.stApp {{
    background-color: #0d1117 !important;
}}

/* -----------------------------------------------------------
   FULL SCREEN OVERLAY BUTTON
   Targeting the specific button by key doesn't work easily in CSS 
   selectors for Streamlit, so we target the First Button in the DOM.
   Since we define it first in Python, this works.
----------------------------------------------------------- */
div.stButton > button {{
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: 999999 !important; /* Always on top */
    
    background-color: {overlay_color} !important;
    
    border: none !important;
    color: transparent !important;
    cursor: default !important; /* Normal cursor so it feels like a screen tap */
    border-radius: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}}

/* Remove hover effects so it doesn't flicker */
div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {{
    background-color: {overlay_color} !important;
    border: none !important;
    color: transparent !important;
    box-shadow: none !important;
}}

/* -----------------------------------------------------------
   DASHBOARD LAYOUT (The "Sci-Fi" Look)
----------------------------------------------------------- */
.block-container {{
    margin: 0 !important;
    margin-top: -55px !important; 
    padding-top: 35px !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
    height: 100vh; 
    min-height: -webkit-fill-available;
    display: flex;
    flex-direction: column;
}}

header, footer, [data-testid="stToolbar"] {{display: none !important;}}

/* Flex Container for the two boxes */
.dashboard-container {{
    height: calc(100vh - 45px); /* Full height minus top padding/gap */
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px; 
    box-sizing: border-box;
}}

/* NAV BOX */
.nav-box {{
    flex: 1; /* Grows to fill space */
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 10px;
    position: relative;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 200px; 
}}

/* TRADE BOX */
.trade-box {{
    flex: 0 0 auto; 
    max-height: 40vh; /* Limits trade box height */
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 10px;
    position: relative;
    display: flex;
    flex-direction: column;
    overflow-y: hidden; /* Hide scrollbar since interaction is disabled */
}}

/* TYPOGRAPHY */
.label-text {{
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    color: #808e9b;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 6px;
    text-transform: uppercase;
    padding-left: 4px;
}}

.screen {{
    background-color: #000000;
    border: 2px solid #2d3436;
    border-radius: 4px;
    box-shadow: inset 0 0 30px rgba(255,255,255,0.02);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}}

.nav-screen-inner {{
    flex: 1;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.nav-value {{
    font-family: 'Orbitron', sans-serif;
    color: #0be881;
    font-weight: 900;
    text-shadow: 0 0 20px rgba(11,232,129,0.4);
    line-height: 1;
    margin-top: -10px; 
}}

/* TABLE STYLING */
.trade-table {{
    width: 100%;
    color: #dcdde1;
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    border-collapse: collapse;
}}
.trade-table th {{ 
    border-bottom: 1px solid #485460; 
    padding: 8px 2px; 
    color: #808e9b; 
    text-align: center;
    background: #050505;
    position: sticky; top: 0;
}}
.trade-table td {{ 
    border-bottom: 1px solid #2d3436; 
    padding: 10px 2px; 
    text-align: center; 
}}

/* DECORATIVE SCREWS */
.screw {{
    position: absolute; width: 6px; height: 6px;
    background: #57606f; border-radius: 50%; 
    border: 1px solid #2f3640;
    z-index: 5;
}}
.tl {{top:6px; left:6px;}} .tr {{top:6px; right:6px;}}
.bl {{bottom:6px; left:6px;}} .br {{bottom:6px; right:6px;}}

/* STATUS COLORS */
.long {{ color: #0be881; }} .short {{ color: #ff3f34; }}
.locked {{ color: #0be881; font-weight: bold; }}
.wait {{ color: #ff9f43; }}
</style>
"""
st.markdown(css_template, unsafe_allow_html=True)

# ==========================================
# 3. OVERLAY BUTTON (RENDER FIRST)
# ==========================================
# This button covers the whole screen due to the CSS above.
st.button(" ", on_click=toggle_secure, key="overlay_btn")

# ==========================================
# 4. DATA ENGINE
# ==========================================
def get_data():
    base = "https://api-fxtrade.oanda.com/v3/accounts" if ENVIRONMENT == "live" else "https://api-fxpractice.oanda.com/v3/accounts"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        r1 = requests.get(f"{base}/{ACCOUNT_ID}/summary", headers=headers, timeout=2)
        r2 = requests.get(f"{base}/{ACCOUNT_ID}/openTrades", headers=headers, timeout=2)
        if r1.status_code == 200 and r2.status_code == 200:
            return r1.json()['account'], r2.json()['trades']
    except:
        pass
    return None, None

# ==========================================
# 5. UI RENDER (BEHIND THE BUTTON)
# ==========================================
acct, trades = get_data()

# --- NAV LOGIC ---
nav_str = "£750" 
if acct: 
    nav_str = f"£{float(acct['NAV']):,.0f}"

# Font Scaling
char_len = len(nav_str)
if char_len <= 4: f_size = "min(25vh, 25vw)"
elif char_len <= 6: f_size = "min(19vh, 19vw)"
elif char_len <= 7: f_size = "min(15vh, 15vw)"
else: f_size = "min(12vh, 12vw)"

# --- TRADES LOGIC ---
rows = ""
if trades:
    for t in trades:
        u, p, pl = float(t['currentUnits']), float(t.get('price', 0)), float(t['unrealizedPL'])
        side, s_cls = ("LONG", "long") if u > 0 else ("SHORT", "short")
        pl_c = "#0be881" if pl >= 0 else "#ff9f43"
        
        tsl, l_s, l_c = "-", "WAIT", "wait"
        if 'trailingStopLossOrder' in t:
            trig = t['trailingStopLossOrder'].get('triggerPrice')
            if trig:
                tv = float(trig)
                tsl = f"{tv:.3f}"
                if (u > 0 and tv > p) or (u < 0 and tv < p):
                    l_s, l_c = "LOCKED", "locked"

        # Construct Table Row HTML
        rows += f"""<tr>
<td class="{s_cls}">{side}</td>
<td>{int(u)}</td>
<td>{t['instrument'].replace('_','/')}</td>
<td style="color:{pl_c}">£{pl:.2f}</td>
<td>{tsl}</td>
<td class="{l_c}">{l_s}</td>
</tr>"""
else:
    rows = "<tr><td colspan='6' style='padding:20px; color:#57606f; font-style:italic;'>NO SIGNAL DETECTED</td></tr>"

# --- FINAL HTML STRUCTURE ---
dashboard_html = f"""
<div class="dashboard-container">
    <div class="nav-box">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>
        <div class="label-text">NAV MONITOR</div>
        <div class="screen nav-screen-inner">
            <div class="nav-value" style="font-size: {f_size};">{nav_str}</div>
        </div>
    </div>

    <div class="trade-box">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>
        <div class="label-text">ACTIVE TRANSMISSIONS</div>
        <div class="screen" style="display:block; padding:0;">
            <table class="trade-table">
                <thead>
                    <tr style="background:#000;">
                        <th>DIR</th><th>UNITS</th><th>INST</th><th>P/L</th><th>TSL</th><th>LOCK</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
</div>
"""

st.markdown(dashboard_html, unsafe_allow_html=True)

# Auto-refresh logic
time.sleep(2)
st.rerun()
