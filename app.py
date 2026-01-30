import streamlit as st
import streamlit.components.v1 as components
import requests
import time

# ==========================================
# 1. CONFIGURATION & STATE
# ==========================================
st.set_page_config(page_title="COMMAND INTERFACE", layout="wide")

if 'secure_mode' not in st.session_state:
    st.session_state.secure_mode = False

if 'trigger_haptic' not in st.session_state:
    st.session_state.trigger_haptic = False

def toggle_secure():
    st.session_state.secure_mode = not st.session_state.secure_mode
    if st.session_state.secure_mode:
        st.session_state.trigger_haptic = True

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
# 2. DATA ENGINE
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

acct, trades = get_data()

real_margin_pct = 0.0
visual_width = 0.0
margin_color = "#0be881" 

if acct:
    nav_float = float(acct.get('NAV', 1))
    margin_used = float(acct.get('marginUsed', 0))
    if nav_float > 0:
        real_margin_pct = (margin_used / nav_float) * 100
    
    # Scale: 50% real margin = 100% full bar
    visual_width = (real_margin_pct / 50) * 100
    if visual_width > 100: visual_width = 100
    
    if real_margin_pct > 30: margin_color = "#ff9f43" 
    if real_margin_pct > 45: margin_color = "#ff3f34" 

# ==========================================
# 3. CSS STYLING
# ==========================================
dash_opacity = "0" if st.session_state.secure_mode else "1"
dash_pointer = "none" if st.session_state.secure_mode else "auto"

css_template = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

.stApp {{ background-color: #000000 !important; overflow: hidden !important; }}
#MainMenu, footer, header {{visibility: hidden !important;}}
[data-testid="stToolbar"] {{display: none !important;}}

.block-container {{
    margin-top: -55px !important; 
    padding: 27px 10px 0 10px !important;
    max-width: 100% !important;
    height: 100vh !important;
    display: flex;
    flex-direction: column;
}}

.dashboard-container {{
    opacity: {dash_opacity};
    pointer-events: {dash_pointer};
    display: flex;
    flex-direction: column;
    gap: 15px;
    height: 100%;
}}

.nav-box, .trade-box {{
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 10px;
    position: relative;
}}

/* --- PROGRESS BAR CLIP LOGIC --- */
.margin-container {{
    position: relative;
    width: 100%;
    height: 34px;
    background: #000;
    border: 1px solid #485460;
    border-radius: 3px;
    overflow: hidden;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 16px;
    margin-top: 5px;
}}

.base-text {{
    position: absolute;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: {margin_color};
    z-index: 1;
}}

.progress-fill {{
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    background-color: {margin_color};
    width: {visual_width}%;
    z-index: 2;
    transition: width 0.5s ease-in-out;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}}

.overlay-text {{
    position: absolute;
    width: 100vw;
    left: 0;
    display: flex;
    justify-content: center;
    color: #000;
}}

.nav-box {{ flex: 1; min-height: 200px; display: flex; flex-direction: column; }}
.trade-box {{ flex: 0 0 auto; max-height: 35vh; overflow: hidden; display: flex; flex-direction: column; }}

.screen {{
    background: #000;
    border: 2px solid #2d3436;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.nav-value {{ font-family: 'Orbitron', sans-serif; color: #0be881; font-weight: 700; }}
.digit-box {{ display: inline-block; width: 0.76em; text-align: center; }}

.trade-table {{ width: 100%; color: #dcdde1; font-family: 'Orbitron', sans-serif; font-size: 11px; border-collapse: collapse; }}
.trade-table th {{ border-bottom: 1px solid #485460; padding: 8px; color: #808e9b; background: #050505; sticky: top; }}
.trade-table td {{ border-bottom: 1px solid #2d3436; padding: 10px; text-align: center; }}

.screw {{ position: absolute; width: 6px; height: 6px; background: #57606f; border-radius: 50%; }}
.tl {{top:6px; left:6px;}} .tr {{top:6px; right:6px;}} .bl {{bottom:6px; left:6px;}} .br {{bottom:6px; right:6px;}}
</style>
"""
st.markdown(css_template, unsafe_allow_html=True)

# ==========================================
# 4. RENDERING
# ==========================================
st.button(" ", on_click=toggle_secure, key="overlay_btn")

val_str = f"{float(acct['NAV']):.0f}" if acct else "0"
char_len = len(val_str) + 1
f_size = "min(20vh, 20vw)" if char_len < 6 else "min(15vh, 15vw)"
nav_html = f'<span style="font-size:50%">£</span>' + "".join([f'<span class="digit-box">{c}</span>' for c in val_str])

rows = ""
if trades:
    for t in trades:
        u, pl = float(t['currentUnits']), float(t['unrealizedPL'])
        side = "LONG" if u > 0 else "SHORT"
        rows += f"<tr><td>{side}</td><td>{u}</td><td>{t['instrument']}</td><td style='color:{'#0be881' if pl >= 0 else '#ff9f43'}'>£{pl:.2f}</td></tr>"
else:
    rows = "<tr><td colspan='4'>NO ACTIVE TRADES</td></tr>"

margin_text = f"{real_margin_pct:.1f}%"

dashboard_html = f"""
<div class="dashboard-container">
    <div class="nav-box">
        <div class="screw tl"></div><div class="screw tr"></div><div class="screw bl"></div><div class="screw br"></div>
        <div style="font-family:'Orbitron'; color:#808e9b; font-size:12px; margin-bottom:5px;">NAV MONITOR</div>
        <div class="screen"><div class="nav-value" style="font-size:{f_size}">{nav_html}</div></div>
    </div>

    <div style="padding:0 5px;">
        <div style="font-family:'Orbitron'; color:#808e9b; font-size:12px;">MARGIN LOAD (MAX 50%)</div>
        <div class="margin-container">
            <div class="base-text">{margin_text}</div>
            <div class="progress-fill">
                <div class="overlay-text">{margin_text}</div>
            </div>
        </div>
    </div>

    <div class="trade-box">
        <div class="screw tl"></div><div class="screw tr"></div><div class="screw bl"></div><div class="screw br"></div>
        <div style="font-family:'Orbitron'; color:#808e9b; font-size:12px; margin-bottom:5px;">TRANSMISSIONS</div>
        <div class="screen" style="display:block; overflow-y:auto;">
            <table class="trade-table">
                <thead><tr><th>DIR</th><th>UNITS</th><th>INST</th><th>P/L</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
</div>
"""

st.markdown(dashboard_html, unsafe_allow_html=True)

time.sleep(2)
st.rerun()
