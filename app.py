import streamlit as st
import requests
import time

# ==========================================
# 1. CONFIGURATION & STATE
# ==========================================
st.set_page_config(page_title="COMMAND INTERFACE", layout="wide")

if 'secure_mode' not in st.session_state:
    st.session_state.secure_mode = False

def toggle_secure():
    st.session_state.secure_mode = not st.session_state.secure_mode

# Secrets Handling
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
# 2. CSS STYLING (Standard String - No Crash)
# ==========================================
css_template = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* GLOBAL RESET */
.stApp {
    background-color: BG_COLOR_PLACEHOLDER !important;
}

/* LAYOUT CONTAINER */
.block-container {
    margin: 0 !important;
    margin-top: -55px !important; /* Hide Streamlit Header */
    
    /* Top Padding remains 35px */
    padding-top: 35px !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
    padding-bottom: 0 !important;
    
    max-width: 100% !important;
    height: 100vh; 
    min-height: -webkit-fill-available;
    display: flex;
    flex-direction: column;
}

/* Hide standard elements */
header, footer, [data-testid="stToolbar"] {display: none !important;}

/* DASHBOARD WRAPPER */
/* HEIGHT CALCULATION: */
/* 35px (Top Gap) + 5px (Bottom Gap) + 70px (Button) = 110px total deduction */
.dashboard-container {
    height: calc(100vh - 110px);
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px; 
    box-sizing: border-box;
}

/* NAV BOX (TOP) - DOMINANT EXPANDER */
.nav-box {
    flex: 1; 
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 10px;
    position: relative;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 200px; 
}

/* TRADE BOX (BOTTOM) - COMPACT */
.trade-box {
    flex: 0 0 auto; 
    max-height: 40vh; 
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 10px;
    position: relative;
    display: flex;
    flex-direction: column;
    overflow-y: auto; 
}

/* BUTTON STYLING (FIXED FOOTER) */
div.stButton {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100% !important;
    z-index: 9999;
    padding: 0 !important;
    margin: 0 !important;
    background-color: BG_COLOR_PLACEHOLDER;
}

div.stButton > button {
    width: 100% !important;
    background-color: #2f3640 !important;
    color: #808e9b !important;
    border: none !important;
    border-top: 2px solid #485460 !important;
    font-family: 'Orbitron', sans-serif !important;
    height: 70px !important;
    font-size: 16px !important;
    letter-spacing: 2px;
    border-radius: 0 !important;
    font-weight: 700;
    text-transform: uppercase;
}

div.stButton > button:hover {
    color: #0be881 !important;
    background-color: #1e272e !important;
}

/* TYPOGRAPHY */
.label-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    color: #808e9b;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 6px;
    text-transform: uppercase;
    padding-left: 4px;
}

.screen {
    background-color: #000000;
    border: 2px solid #2d3436;
    border-radius: 4px;
    box-shadow: inset 0 0 30px rgba(255,255,255,0.02);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

.nav-screen-inner {
    flex: 1;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.nav-value {
    font-family: 'Orbitron', sans-serif;
    font-size: min(25vh, 25vw); 
    color: #0be881;
    font-weight: 900;
    text-shadow: 0 0 20px rgba(11,232,129,0.4);
    line-height: 1;
    margin-top: -10px; 
}

/* TABLE */
.trade-table {
    width: 100%;
    color: #dcdde1;
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    border-collapse: collapse;
}
.trade-table th { 
    border-bottom: 1px solid #485460; 
    padding: 8px 2px; 
    color: #808e9b; 
    text-align: center;
    background: #050505;
    position: sticky; top: 0;
}
.trade-table td { 
    border-bottom: 1px solid #2d3436; 
    padding: 10px 2px; 
    text-align: center; 
}

/* SCREWS */
.screw {
    position: absolute; width: 6px; height: 6px;
    background: #57606f; border-radius: 50%; 
    border: 1px solid #2f3640;
    z-index: 5;
}
.tl {top:6px; left:6px;} .tr {top:6px; right:6px;}
.bl {bottom:6px; left:6px;} .br {bottom:6px; right:6px;}

.long { color: #0be881; } .short { color: #ff3f34; }
.locked { color: #0be881; font-weight: bold; }
.wait { color: #ff9f43; }
</style>
"""

# Inject Dynamic Background Color
bg_color = "#000000" if st.session_state.secure_mode else "#0d1117"
st.markdown(css_template.replace("BG_COLOR_PLACEHOLDER", bg_color), unsafe_allow_html=True)

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
# 4. UI RENDER
# ==========================================

if st.session_state.secure_mode:
    btn_label = "👁️ ACTIVATE SYSTEM"
else:
    btn_label = "🔒 SECURE SYSTEM"

st.button(btn_label, on_click=toggle_secure)

if not st.session_state.secure_mode:
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

            # FLUSH LEFT HTML
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

    # HTML STRING - FLUSH LEFT
    dashboard_html = f"""
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
"""
    st.markdown(dashboard_html, unsafe_allow_html=True)

    time.sleep(2)
    st.rerun()
