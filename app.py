import streamlit as st
import requests
import time

# ==========================================
# 1. CONFIGURATION & STATE
# ==========================================
st.set_page_config(page_title="COMMAND INTERFACE", layout="wide")

# Initialize session state
# secure_mode = False -> System is ACTIVE (Visible)
# secure_mode = True  -> System is SECURE (Hidden/Blackout)
if 'secure_mode' not in st.session_state:
    st.session_state.secure_mode = False

def toggle_secure():
    st.session_state.secure_mode = not st.session_state.secure_mode

# Secrets handling
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
# 2. CSS STYLING (RESPONSIVE & FULL WIDTH)
# ==========================================
bg_color = "#000000" if st.session_state.secure_mode else "#0d1117"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* RESET STREAMLIT DEFAULTS */
.stApp {{
    background-color: {bg_color} !important;
}}

/* MAIN CONTAINER - FLEX COLUMN LAYOUT */
.block-container {{
    padding: 0.5rem 0.5rem 0 0.5rem !important;
    max-width: 100% !important;
    margin: 0 auto;
    /* Use standard viewport height, fallback for mobile browsers */
    min-height: 100vh; 
    min-height: -webkit-fill-available;
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

/* HIDE HEADER/FOOTER */
header, footer, [data-testid="stToolbar"] {{display: none !important;}}

/* DASHBOARD WRAPPER - FILLS SPACE ABOVE BUTTON */
.dashboard-container {{
    flex: 1; 
    display: flex;
    flex-direction: column;
    width: 100%;
    gap: 10px;
    overflow: hidden;
}}

/* NAV BOX (TOP) */
.nav-box {{
    flex: 4; /* Takes more vertical space */
    min-height: 200px;
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 10px;
    position: relative;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
}}

/* TRADE BOX (BOTTOM) */
.trade-box {{
    flex: 3; /* Takes less vertical space */
    min-height: 150px;
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 10px;
    position: relative;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}}

/* BUTTON STYLES - FIXED BOTTOM FEEL */
div.stButton {{
    width: 100%;
    margin-bottom: 10px; /* Small padding from bottom edge */
}}

div.stButton > button {{
    width: 100% !important;
    background-color: #2f3640 !important;
    color: #808e9b !important;
    border: 1px solid #485460 !important;
    font-family: 'Orbitron', sans-serif !important;
    height: 60px !important;
    font-size: 16px !important;
    letter-spacing: 2px;
    border-radius: 6px !important;
    font-weight: 700;
    text-transform: uppercase;
}}

div.stButton > button:hover {{
    border-color: #0be881 !important;
    color: #0be881 !important;
    background-color: #1e272e !important;
    box-shadow: 0 0 15px rgba(11, 232, 129, 0.2);
}}

div.stButton > button:active {{
    background-color: #000 !important;
    border-color: #fff !important;
    color: #fff !important;
}}

/* UI ELEMENTS */
.label-text {{
    font-family: 'Orbitron', sans-serif;
    font-size: 12px;
    color: #808e9b;
    font-weight: 900;
    letter-spacing: 1px;
    margin-bottom: 8px;
    text-transform: uppercase;
    padding-left: 5px;
}}

.screen {{
    background-color: #000000;
    border: 2px solid #2d3436;
    border-radius: 4px;
    box-shadow: inset 0 0 30px rgba(255,255,255,0.02);
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}}

.nav-value {{
    font-family: 'Orbitron', sans-serif;
    /* Responsive font size: 18% of width, capped at 160px for desktops */
    font-size: min(18vw, 160px); 
    color: #0be881;
    font-weight: 900;
    text-shadow: 0 0 20px rgba(11,232,129,0.4);
    line-height: 1;
    margin-top: -10px; /* Visual centering adjustment */
}}

/* TRADE TABLE */
.trade-table {{
    width: 100%;
    color: #dcdde1;
    font-family: 'Orbitron', sans-serif;
    font-size: 11px; /* Smaller font for mobile tables */
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

/* DECORATION */
.screw {{
    position: absolute; width: 6px; height: 6px;
    background: #57606f; border-radius: 50%; 
    border: 1px solid #2f3640;
    z-index: 5;
}}
.tl {{top:6px; left:6px;}} .tr {{top:6px; right:6px;}}
.bl {{bottom:6px; left:6px;}} .br {{bottom:6px; right:6px;}}

/* COLORS */
.long {{ color: #0be881; }} .short {{ color: #ff3f34; }}
.locked {{ color: #0be881; font-weight: bold; }}
.wait {{ color: #ff9f43; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA LOGIC
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
# 4. RENDER UI
# ==========================================

# Determine content based on Secure Mode
if st.session_state.secure_mode:
    # HIDDEN STATE
    btn_label = "👁️ ACTIVATE SYSTEM"
    nav_str = ""
    rows = ""
    opacity = "0"
else:
    # VISIBLE STATE
    btn_label = "🔒 SECURE SYSTEM"
    opacity = "1"
    
    acct, trades = get_data()
    nav_str = "£750" 
    if acct: 
        nav_str = f"£{float(acct['NAV']):,.0f}"

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

            # FLUSH LEFT HTML STRING - DO NOT INDENT
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

# MAIN DISPLAY (FLUSH LEFT)
st.markdown(f"""
<div class="dashboard-container">
<div class="nav-box">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">NAV MONITOR</div>
<div class="screen">
<div class="nav-value" style="opacity: {opacity}; transition: opacity 0.2s;">{nav_str}</div>
</div>
</div>
<div class="trade-box">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">ACTIVE TRANSMISSIONS</div>
<div class="screen" style="display:block; padding:0; overflow-y:auto;">
<table class="trade-table" style="opacity: {opacity}; transition: opacity 0.2s;">
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
""", unsafe_allow_html=True)

# BOTTOM BUTTON
st.button(btn_label, on_click=toggle_secure)

# AUTO REFRESH
time.sleep(2)
st.rerun()
