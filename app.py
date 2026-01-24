import streamlit as st
import requests
import time

# ==========================================
# 1. CONFIGURATION & STATE
# ==========================================
try:
    ACCOUNT_ID = st.secrets["ACCOUNT_ID"]
    API_TOKEN = st.secrets["API_TOKEN"]
    ENVIRONMENT = st.secrets["ENVIRONMENT"]
except FileNotFoundError:
    st.error("Secrets missing.")
    st.stop()

st.set_page_config(page_title="COMMAND INTERFACE", layout="wide")

# Initialize Session State for Stealth Mode
if 'stealth_mode' not in st.session_state:
    st.session_state.stealth_mode = False

def toggle_stealth():
    st.session_state.stealth_mode = not st.session_state.stealth_mode

# ==========================================
# 2. STYLING (CSS)
# ==========================================
# We adjust the background dynamically based on mode
bg_color = "#000000" if st.session_state.stealth_mode else "#0d1117"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* GLOBAL SETTINGS */
.stApp {{
    background-color: {bg_color} !important;
}}
.block-container {{
    padding: 1rem !important;
    max-width: 600px !important;
    margin: 0 auto;
    height: 95vh;
    display: flex;
    flex-direction: column;
}}
header, footer {{display: none !important;}}

/* HIDE STREAMLIT BUTTON STYLING */
div.stButton > button:first-child {{
    width: 100%;
    background-color: #2f3640;
    color: #808e9b;
    border: 1px solid #485460;
    font-family: 'Orbitron', sans-serif;
    height: 50px;
    margin-top: 10px;
}}
div.stButton > button:hover {{
    border-color: #0be881;
    color: #0be881;
}}

/* METAL PANELS (Visible only in active mode) */
.metal-panel {{
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 8px;
    position: relative;
    margin-bottom: 10px;
    display: flex;
    flex-direction: column;
    padding: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.8);
}}

/* FLEX SPACING */
.nav-box {{ flex: 5; }}
.trade-box {{ flex: 4; }}

/* SCREENS */
.screen {{
    background-color: #000000;
    border: 2px solid #2d3436;
    flex-grow: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 5px;
    box-shadow: inset 0 0 20px rgba(255,255,255,0.05);
}}

/* TEXT */
.label-text {{
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    color: #808e9b;
    font-weight: 800;
    letter-spacing: 1px;
}}
.nav-value {{
    font-family: 'Orbitron', sans-serif;
    font-size: 15vw;
    color: #0be881;
    text-shadow: 0 0 20px rgba(11,232,129,0.4);
}}
@media (min-width: 600px) {{ .nav-value {{ font-size: 80px; }} }}

/* TABLE */
.trade-table {{
    width: 100%;
    color: #dcdde1;
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    border-collapse: collapse;
}}
.trade-table th {{ border-bottom: 1px solid #485460; padding: 5px; color: #808e9b; }}
.trade-table td {{ border-bottom: 1px solid #2d3436; padding: 8px 4px; text-align: center; }}
.long {{ color: #0be881; }}
.short {{ color: #ff3f34; }}
.locked {{ color: #0be881; font-weight: bold; }}
.wait {{ color: #ff9f43; }}

/* SCREWS */
.screw {{
    position: absolute;
    width: 6px; height: 6px;
    background: #57606f; border-radius: 50%;
    border: 1px solid #2f3640;
}}
.tl {{top:5px; left:5px;}} .tr {{top:5px; right:5px;}}
.bl {{bottom:5px; left:5px;}} .br {{bottom:5px; right:5px;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA ENGINE
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

# A. STEALTH MODE (Black Screen)
if st.session_state.stealth_mode:
    # Spacer to push button to bottom
    st.markdown("<div style='flex:1;'></div>", unsafe_allow_html=True)
    
    # The Wake Button
    st.button("👁️ ACTIVATE SYSTEM", on_click=toggle_stealth)

# B. ACTIVE MODE (Full UI)
else:
    acct, trades = get_data()
    
    # 1. NAV PANEL
    nav_str = "---"
    if acct: nav_str = f"£{float(acct['NAV']):,.0f}"

    st.markdown(f"""
    <div class="metal-panel nav-box">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>
        <div class="label-text">NAV MONITOR</div>
        <div class="screen">
            <div class="nav-value">{nav_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. TRADES PANEL
    rows = ""
    if trades:
        for t in trades:
            u = float(t['currentUnits'])
            p = float(t.get('price', 0))
            pl = float(t['unrealizedPL'])
            
            side = "LONG" if u > 0 else "SHORT"
            s_cls = "long" if u > 0 else "short"
            pl_c = "#0be881" if pl >= 0 else "#ff9f43"
            
            tsl, lock_s, lock_c = "-", "WAIT", "wait"
            if 'trailingStopLossOrder' in t:
                trig = t['trailingStopLossOrder'].get('triggerPrice')
                if trig:
                    tv = float(trig)
                    tsl = f"{tv:.3f}"
                    if (u > 0 and tv > p) or (u < 0 and tv < p):
                        lock_s, lock_c = "LOCKED", "locked"

            rows += f"""<tr>
                <td class="{s_cls}">{side}</td>
                <td>{int(u)}</td>
                <td>{t['instrument'].replace('_','/')}</td>
                <td style="color:{pl_c}">£{pl:.2f}</td>
                <td>{tsl}</td>
                <td class="{lock_c}">{lock_s}</td>
            </tr>"""
    else:
        rows = "<tr><td colspan='6' style='padding:30px 0; color:#57606f;'>NO SIGNAL</td></tr>"

    st.markdown(f"""
    <div class="metal-panel trade-box">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>
        <div class="label-text">ACTIVE TRANSMISSIONS</div>
        <div class="screen" style="overflow-y:auto; display:block;">
            <table class="trade-table">
                <thead><tr><th>DIR</th><th>UNITS</th><th>INST</th><th>P/L</th><th>TSL</th><th>LOCK</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. TOGGLE BUTTON
    st.button("⚫ BLACKOUT MODE", on_click=toggle_stealth)

# ==========================================
# 5. AUTO-REFRESH LOGIC
# ==========================================
# We sleep, then rerun. This replaces 'while True' and makes buttons responsive.
time.sleep(2)
st.rerun()
