import streamlit as st
import requests
import time

# ==========================================
# 1. CONFIGURATION & STATE
# ==========================================
st.set_page_config(page_title="COMMAND INTERFACE", layout="wide")

# Initialize session state for the security toggle
# secure_mode = False means the system is ACTIVE (Visible)
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
# 2. CSS STYLING (DESKTOP REPLICA)
# ==========================================
bg_color = "#000000" if st.session_state.secure_mode else "#0d1117"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* GLOBAL SETTINGS */
.stApp {{
    background-color: {bg_color} !important;
}}

/* LAYOUT RESET - REMOVE PADDING TO ALLOW FULL WIDTH/HEIGHT */
.block-container {{
    padding: 1rem 1rem 0 1rem !important;
    max-width: 100% !important;
    margin: 0 auto;
    height: 100vh;
    display: flex;
    flex-direction: column;
    gap: 0 !important;
}}

/* HIDE DEFAULT STREAMLIT ELEMENTS */
header, footer, [data-testid="stToolbar"] {{display: none !important;}}

/* DASHBOARD CONTAINER - FLEX COLUMNS */
.dashboard-container {{
    flex: 1;
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-bottom: 10px;
    gap: 15px;
}}

/* NAV BOX (Top Panel) - TALLER */
.nav-box {{
    flex: 3; /* Takes up 3 parts of space */
    min-height: 200px;
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 4px;
    padding: 8px;
    position: relative;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
}}

/* TRADE BOX (Bottom Panel) - SHORTER */
.trade-box {{
    flex: 2; /* Takes up 2 parts of space */
    min-height: 150px;
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 4px;
    padding: 8px;
    position: relative;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}}

/* BUTTON STYLES - FULL WIDTH STRIP */
/* This targets the container of the button to ensure it fills width */
.stButton {{
    width: 100%;
    padding-bottom: 10px;
}}
/* This targets the actual button element */
.stButton > button {{
    width: 100% !important;
    background-color: #2f3640 !important;
    color: #808e9b !important;
    border: 1px solid #485460 !important;
    font-family: 'Orbitron', sans-serif !important;
    height: 50px !important;
    font-size: 14px !important;
    letter-spacing: 2px;
    border-radius: 4px !important;
    margin-top: 0px !important;
    font-weight: 700;
}}
.stButton > button:hover {{
    border-color: #0be881 !important;
    color: #0be881 !important;
    background-color: #1e272e !important;
    box-shadow: 0 0 15px rgba(11, 232, 129, 0.1);
}}

/* TYPOGRAPHY */
.label-text {{
    font-family: 'Orbitron', sans-serif;
    font-size: 14px;
    color: #808e9b;
    font-weight: 900;
    letter-spacing: 1px;
    margin-bottom: 8px;
    text-transform: uppercase;
    padding-left: 10px;
}}

.screen {{
    background-color: #000000;
    border: 2px solid #2d3436;
    border-radius: 2px;
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
    font-size: 15vw; /* Responsive huge text */
    color: #0be881;
    font-weight: 900;
    text-shadow: 0 0 20px rgba(11,232,129,0.4);
    z-index: 2;
    line-height: 1;
}}
@media (min-width: 1000px) {{ .nav-value {{ font-size: 180px; }} }}

/* TABLE STYLES */
.trade-table {{
    width: 100%;
    border-collapse: collapse;
    color: #dcdde1;
    font-family: 'Orbitron', sans-serif;
    font-size: 12px;
}}
.trade-table th {{ 
    border-bottom: 1px solid #485460; 
    padding: 8px; 
    color: #808e9b; 
    text-align: center;
    background: #050505;
    position: sticky; top: 0;
}}
.trade-table td {{ 
    border-bottom: 1px solid #2d3436; 
    padding: 8px 4px; 
    text-align: center; 
}}

/* DECORATIVE SCREWS */
.screw {{
    position: absolute; width: 8px; height: 8px;
    background: #57606f; border-radius: 50%; 
    border: 1px solid #2f3640;
    z-index: 5;
}}
.tl {{top:8px; left:8px;}} .tr {{top:8px; right:8px;}}
.bl {{bottom:8px; left:8px;}} .br {{bottom:8px; right:8px;}}

/* STATUS COLORS */
.long {{ color: #0be881; }} .short {{ color: #ff3f34; }}
.locked {{ color: #0be881; font-weight: bold; text-shadow: 0 0 5px #0be881; }}
.wait {{ color: #ff9f43; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA & LOGIC
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
# 4. UI RENDERING
# ==========================================

# Determine State
if st.session_state.secure_mode:
    # SECURE MODE (Hidden)
    btn_label = "👁️ ACTIVATE SYSTEM"
    nav_str = ""
    rows = ""
    screen_opacity = "0"
else:
    # ACTIVE MODE (Visible)
    btn_label = "🔒 SECURE SYSTEM"
    screen_opacity = "1"
    
    acct, trades = get_data()
    nav_str = "£750" # Default
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

            # WARNING: KEEP HTML FLUSH LEFT. DO NOT INDENT.
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

# RENDER HTML
# The indentation here is deliberately removed to prevent the "Code Block" bug.
st.markdown(f"""
<div class="dashboard-container">
<div class="nav-box">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">NAV MONITOR</div>
<div class="screen">
<div class="nav-value" style="opacity: {screen_opacity}; transition: opacity 0.2s;">{nav_str}</div>
</div>
</div>
<div class="trade-box">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">ACTIVE TRANSMISSIONS</div>
<div class="screen" style="display:block; padding:0; overflow-y:auto;">
<table class="trade-table" style="opacity: {screen_opacity}; transition: opacity 0.2s;">
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

# RENDER BUTTON
st.button(btn_label, on_click=toggle_secure)

# AUTO REFRESH
time.sleep(2)
st.rerun()
