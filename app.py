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
# 2. DYNAMIC FLEXBOX STYLING (CSS)
# ==========================================
bg_color = "#000000" if st.session_state.stealth_mode else "#0d1117"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* --- MAIN CONTAINER SETUP --- */
.stApp {{
    background-color: {bg_color} !important;
    overflow: hidden; /* Prevent double scrollbars */
}}

.block-container {{
    padding: 0.5rem !important;
    max-width: 600px !important;
    margin: 0 auto;
    height: 98vh; /* Force app to fit screen height */
    display: flex;
    flex-direction: column;
}}

/* Hide header/footer */
header, footer {{display: none !important;}}

/* --- THE FLEX LAYOUT ENGINE --- */
/* This container holds the two boxes */
.dashboard-container {{
    flex: 1; /* Take up all space above the button */
    display: flex;
    flex-direction: column;
    overflow: hidden; 
    margin-bottom: 10px;
}}

/* BOX 1: NAV (The Flexible Giant) */
.nav-box {{
    flex-grow: 1; /* Grow to fill ALL available empty space */
    flex-shrink: 1; /* Allow shrinking if trades push up */
    min-height: 200px; /* Don't squash smaller than this */
    
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    position: relative;
    margin-bottom: 10px;
    transition: all 0.3s ease; /* Smooth animation when resizing */
}}

/* BOX 2: TRADES (The Content Sized) */
.trade-box {{
    flex-grow: 0; /* Do not grow arbitrarily */
    flex-shrink: 0; 
    height: auto; /* Height is determined by content */
    max-height: 50vh; /* Cap at 50% screen height so NAV doesn't disappear */
    
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow-y: auto; /* Scroll internally if it hits max-height */
}}

/* --- BUTTON STYLING (Full Width) --- */
div.stButton > button:first-child {{
    width: 100%;
    background-color: #2f3640;
    color: #808e9b;
    border: 1px solid #485460;
    font-family: 'Orbitron', sans-serif;
    height: 60px;
    font-size: 14px;
    border-radius: 8px;
    margin-top: auto; /* Push to very bottom if flex allows */
}}
div.stButton > button:hover {{
    border-color: #0be881;
    color: #0be881;
    background-color: #1e272e;
}}

/* --- COMPONENT STYLING --- */
.screen {{
    background-color: #000000;
    border: 2px solid #2d3436;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 0 20px rgba(255,255,255,0.05);
}}

/* Nav Screen fills the Nav Box */
.nav-screen-inner {{
    flex: 1;
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
# 4. RENDER UI
# ==========================================

if st.session_state.stealth_mode:
    # Full height spacer to push button down
    st.markdown("<div style='height: 85vh;'></div>", unsafe_allow_html=True)
    st.button("👁️ ACTIVATE SYSTEM", on_click=toggle_stealth)

else:
    acct, trades = get_data()
    
    # --- PREPARE CONTENT ---
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

    # --- RENDER FLEXBOX LAYOUT ---
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

    # BUTTON (Outside the flex container, sits at bottom)
    st.button("⚫ BLACKOUT MODE", on_click=toggle_stealth)

# Refresh logic
time.sleep(2)
st.rerun()
