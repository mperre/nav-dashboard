import streamlit as st
import requests
import time

# ==========================================
# 1. CONFIGURATION & STATE
# ==========================================
try:
    if "ACCOUNT_ID" in st.secrets:
        ACCOUNT_ID = st.secrets["ACCOUNT_ID"]
        API_TOKEN = st.secrets["API_TOKEN"]
        ENVIRONMENT = st.secrets["ENVIRONMENT"]
    else:
        # Dummy fallback
        ACCOUNT_ID = "000-000-0000000-000"
        API_TOKEN = "token"
        ENVIRONMENT = "practice"
except FileNotFoundError:
    st.error("Secrets missing.")
    st.stop()

st.set_page_config(page_title="COMMAND INTERFACE", layout="wide")

if 'stealth_mode' not in st.session_state:
    st.session_state.stealth_mode = False

def toggle_stealth():
    st.session_state.stealth_mode = not st.session_state.stealth_mode

# ==========================================
# 2. CSS STYLING
# ==========================================
bg_color = "#000000" if st.session_state.stealth_mode else "#0d1117"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* GLOBAL SETTINGS */
.stApp {{
    background-color: {bg_color} !important;
}}

/* REMOVE PADDING TO ALLOW FULL WIDTH/HEIGHT */
.block-container {{
    padding: 1rem 1rem 0 1rem !important;
    max-width: 100% !important;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 0 !important;
}}

/* HIDE STREAMLIT UI ELEMENTS */
header, footer, [data-testid="stToolbar"] {{display: none !important;}}

/* DASHBOARD LAYOUT */
.dashboard-container {{
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-bottom: 15px; /* Space between boxes and button */
}}

/* BOX STYLES */
.nav-box, .trade-box {{
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 4px;
    padding: 10px;
    position: relative;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
}}

.nav-box {{
    min-height: 200px;
    margin-bottom: 10px;
}}

.trade-box {{
    min-height: 150px;
    height: auto;
}}

/* BUTTON STYLES - FORCE FULL WIDTH */
.stButton {{
    width: 100% !important;
}}
.stButton > button {{
    width: 100% !important;
    background-color: #2f3640 !important;
    color: #808e9b !important;
    border: 1px solid #485460 !important;
    font-family: 'Orbitron', sans-serif !important;
    height: 60px !important;
    font-size: 16px !important;
    border-radius: 4px !important;
    margin-top: 0px !important;
}}
.stButton > button:hover {{
    border-color: #0be881 !important;
    color: #0be881 !important;
    background-color: #1e272e !important;
}}

/* TYPOGRAPHY & SCREENS */
.label-text {{
    font-family: 'Orbitron', sans-serif;
    font-size: 12px;
    color: #808e9b;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 5px;
    text-transform: uppercase;
}}

.screen {{
    background-color: #000000;
    border: 2px solid #2d3436;
    border-radius: 2px;
    box-shadow: inset 0 0 20px rgba(255,255,255,0.05);
}}

.nav-value {{
    font-family: 'Orbitron', sans-serif;
    font-size: 100px; /* Big fixed size for desktop feel */
    color: #0be881;
    font-weight: 900;
    text-align: center;
    width: 100%;
    line-height: 1.2;
    text-shadow: 0 0 20px rgba(11,232,129,0.4);
}}

/* TABLE STYLES */
.trade-table {{
    width: 100%;
    color: #dcdde1;
    font-family: 'Orbitron', sans-serif;
    font-size: 12px;
    border-collapse: collapse;
}}
.trade-table th {{ border-bottom: 1px solid #485460; padding: 10px; color: #808e9b; text-align: center; }}
.trade-table td {{ border-bottom: 1px solid #2d3436; padding: 12px 4px; text-align: center; }}

/* SCREWS */
.screw {{
    position: absolute; width: 6px; height: 6px;
    background: #57606f; border-radius: 50%; border: 1px solid #2f3640;
}}
.tl {{top:6px; left:6px;}} .tr {{top:6px; right:6px;}}
.bl {{bottom:6px; left:6px;}} .br {{bottom:6px; right:6px;}}

/* UTILS */
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
# 4. RENDER UI
# ==========================================

if st.session_state.stealth_mode:
    st.markdown("<div style='flex:1;'></div>", unsafe_allow_html=True)
    st.button("👁️ ACTIVATE SYSTEM", on_click=toggle_stealth)

else:
    acct, trades = get_data()
    
    # Fallback data for display
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

            # IMPORTANT: NO INDENTATION INSIDE THIS STRING
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

    # IMPORTANT: The HTML string below is flush left (no indentation) 
    # to prevent Streamlit from interpreting it as a code block.
    st.markdown(f"""
<div class="dashboard-container">
<div class="nav-box">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">NAV MONITOR</div>
<div class="screen" style="flex:1; display:flex; align-items:center; justify-content:center;">
<div class="nav-value">{nav_str}</div>
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
""", unsafe_allow_html=True)

    st.button("⚫ BLACKOUT MODE", on_click=toggle_stealth)

time.sleep(2)
st.rerun()
