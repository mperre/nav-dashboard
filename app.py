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

if 'stealth_mode' not in st.session_state:
    st.session_state.stealth_mode = False

def toggle_stealth():
    st.session_state.stealth_mode = not st.session_state.stealth_mode

# ==========================================
# 2. CSS STYLING (FLEXBOX LAYOUT)
# ==========================================
bg_color = "#000000" if st.session_state.stealth_mode else "#0d1117"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* GLOBAL APP SETTINGS */
.stApp {{
    background-color: {bg_color} !important;
}}

/* MAIN CONTAINER - FLEX COLUMN */
.block-container {{
    padding: 0.5rem !important;
    max-width: 600px !important;
    margin: 0 auto;
    height: 98vh; /* Fill the screen */
    display: flex;
    flex-direction: column;
}}

/* HIDE HEADER/FOOTER */
header, footer {{display: none !important;}}

/* DASHBOARD WRAPPER */
.dashboard-container {{
    flex: 1; 
    display: flex;
    flex-direction: column;
    overflow: hidden; 
    margin-bottom: 10px;
}}

/* NAV BOX - THE FLEXIBLE GIANT */
.nav-box {{
    flex-grow: 1;  /* This forces it to expand */
    flex-shrink: 1;
    min-height: 150px;
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    position: relative;
    margin-bottom: 10px;
}}

/* TRADE BOX - CONTENT SIZED */
.trade-box {{
    flex-grow: 0;
    flex-shrink: 0;
    height: auto;
    max-height: 60vh;
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow-y: auto;
}}

/* BUTTON STYLING (FULL WIDTH) */
div.stButton {{
    width: 100%;
}}
div.stButton > button {{
    width: 100% !important;
    background-color: #2f3640;
    color: #808e9b;
    border: 1px solid #485460;
    font-family: 'Orbitron', sans-serif;
    height: 60px;
    font-size: 14px;
    border-radius: 8px;
    display: block;
}}
div.stButton > button:hover {{
    border-color: #0be881;
    color: #0be881;
    background-color: #1e272e;
}}

/* SCREENS & TEXT */
.screen {{
    background-color: #000000;
    border: 2px solid #2d3436;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 0 20px rgba(255,255,255,0.05);
}}
.nav-screen-inner {{
    flex: 1; /* Fill the NAV box */
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 5px;
}}

.trade-table {{
    width: 100%;
    color: #dcdde1;
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    border-collapse: collapse;
}}
.trade-table th {{ border-bottom: 1px solid #485460; padding: 8px; color: #808e9b; text-align: center; }}
.trade-table td {{ border-bottom: 1px solid #2d3436; padding: 10px 4px; text-align: center; }}

.nav-value {{
    font-family: 'Orbitron', sans-serif;
    font-size: 15vw;
    color: #0be881;
    font-weight: 900;
    text-shadow: 0 0 20px rgba(11,232,129,0.4);
}}
@media (min-width: 600px) {{ .nav-value {{ font-size: 90px; }} }}

.label-text {{
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    color: #808e9b;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 5px;
}}

.screw {{
    position: absolute; width: 6px; height: 6px;
    background: #57606f; border-radius: 50%; border: 1px solid #2f3640;
}}
.tl {{top:6px; left:6px;}} .tr {{top:6px; right:6px;}}
.bl {{bottom:6px; left:6px;}} .br {{bottom:6px; right:6px;}}
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
# 4. RENDER UI (STRICT FLUSH LEFT HTML)
# ==========================================

if st.session_state.stealth_mode:
    # Spacer to push button to bottom
    st.markdown("<div style='flex:1;'></div>", unsafe_allow_html=True)
    st.button("👁️ ACTIVATE SYSTEM", on_click=toggle_stealth)

else:
    acct, trades = get_data()
    
    nav_str = "---"
    if acct: nav_str = f"£{float(acct['NAV']):,.0f}"

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

            # WARNING: DO NOT INDENT THIS HTML STRING
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

    # WARNING: DO NOT INDENT THE HTML BELOW. IT MUST TOUCH THE LEFT MARGIN.
    st.markdown(f"""
<div class="dashboard-container">
<div class="nav-box">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">NAV MONITOR</div>
<div class="screen nav-screen-inner">
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

    # The button sits outside the HTML block to ensure full width
    st.button("⚫ BLACKOUT MODE", on_click=toggle_stealth)

time.sleep(2)
st.rerun()
