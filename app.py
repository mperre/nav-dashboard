import streamlit as st
import requests
import time

# ==========================================
# 1. CONFIGURATION & SECRETS
# ==========================================
try:
    ACCOUNT_ID = st.secrets["ACCOUNT_ID"]
    API_TOKEN = st.secrets["API_TOKEN"]
    ENVIRONMENT = st.secrets["ENVIRONMENT"]
except FileNotFoundError:
    st.error("Secrets not found. Please check your Streamlit settings.")
    st.stop()

st.set_page_config(page_title="COMMAND INTERFACE", layout="centered")

# ==========================================
# 2. EXACT CSS STYLING (Desktop Replica)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* GLOBAL BACKGROUND - Deep Dark Slate */
.stApp {
    background-color: #0d1117 !important;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 5rem;
    max-width: 450px; /* Mobile width constraint */
}
header {visibility: hidden;}
footer {visibility: hidden;}

/* THE METAL PANEL */
.metal-panel {
    background-color: #1e272e; /* Dark Slate Blue */
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 15px;
    position: relative;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.6);
}

/* SCREWS IN CORNERS */
.screw {
    position: absolute;
    width: 8px;
    height: 8px;
    background-color: #57606f;
    border-radius: 50%;
    border: 1px solid #2f3640;
    box-shadow: inset 1px 1px 2px rgba(255,255,255,0.2);
}
.tl { top: 6px; left: 6px; }
.tr { top: 6px; right: 6px; }
.bl { bottom: 6px; left: 6px; }
.br { bottom: 6px; right: 6px; }

/* BLACK INSET SCREEN */
.black-screen {
    background-color: #000000;
    border: 2px solid #2d3436;
    margin-top: 5px;
    padding: 15px 5px;
    text-align: center;
    box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.05);
}

/* TEXT STYLES */
.label-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    color: #808e9b; /* Muted Grey-Blue */
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    text-shadow: 1px 1px 0px #000;
}

.nav-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 60px;
    color: #0be881; /* Bright Green */
    font-weight: 900;
    text-shadow: 0 0 20px rgba(11, 232, 129, 0.3);
    margin: 10px 0;
}

/* TABLE STYLES */
.trade-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    color: #dcdde1;
}
.trade-table th {
    color: #808e9b;
    padding: 6px 2px;
    border-bottom: 1px solid #485460;
    text-align: center;
    font-weight: 700;
}
.trade-table td {
    padding: 8px 2px;
    text-align: center;
    border-bottom: 1px solid #2d3436;
}

/* COLORS */
.long { color: #0be881; }
.short { color: #ff3f34; }
.profit-yes { color: #0be881; font-weight: bold; text-shadow: 0 0 5px #0be881; }
.profit-wait { color: #ff9f43; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA ENGINE
# ==========================================
def get_data():
    base = "https://api-fxtrade.oanda.com/v3/accounts" if ENVIRONMENT == "live" else "https://api-fxpractice.oanda.com/v3/accounts"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        r1 = requests.get(f"{base}/{ACCOUNT_ID}/summary", headers=headers, timeout=3)
        r2 = requests.get(f"{base}/{ACCOUNT_ID}/openTrades", headers=headers, timeout=3)
        if r1.status_code == 200 and r2.status_code == 200:
            return r1.json()['account'], r2.json()['trades']
    except:
        pass
    return None, None

# ==========================================
# 4. MAIN LOOP (FLUSH LEFT HTML)
# ==========================================
placeholder = st.empty()

while True:
    acct, trades = get_data()
    
    with placeholder.container():
        
        # --- TOP PANEL: NAV ---
        nav_val = "---"
        if acct:
            nav_val = f"£{float(acct['NAV']):,.0f}"

        # HTML MUST BE FLUSH LEFT TO AVOID CODE BLOCKS
        st.markdown(f"""
<div class="metal-panel">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">NAV MONITOR</div>
<div class="black-screen">
<div class="nav-text">{nav_val}</div>
</div>
</div>
""", unsafe_allow_html=True)

        # --- BOTTOM PANEL: TRADES ---
        rows = ""
        if trades:
            for t in trades:
                units = float(t['currentUnits'])
                entry = float(t.get('price', 0))
                pl = float(t['unrealizedPL'])
                
                # Colors & Direction
                side = "LONG" if units > 0 else "SHORT"
                side_class = "long" if units > 0 else "short"
                pl_color = "#0be881" if pl >= 0 else "#ff9f43"
                
                # TSL Lock Logic
                tsl_str = "-"
                lock_str = "WAIT"
                lock_class = "profit-wait"
                
                if 'trailingStopLossOrder' in t:
                    trigger = t['trailingStopLossOrder'].get('triggerPrice')
                    if trigger:
                        trig_val = float(trigger)
                        tsl_str = f"{trig_val:.3f}"
                        # Logic: Is TSL better than Entry?
                        if (units > 0 and trig_val > entry) or (units < 0 and trig_val < entry):
                            lock_str = "LOCKED"
                            lock_class = "profit-yes"

                rows += f"""
                <tr>
                    <td class="{side_class}">{side}</td>
                    <td>{int(units)}</td>
                    <td>{t['instrument'].replace('_','/')}</td>
                    <td style="color:{pl_color}">£{pl:.2f}</td>
                    <td>{tsl_str}</td>
                    <td class="{lock_class}">{lock_str}</td>
                </tr>"""
        else:
            rows = """<tr><td colspan="6" style="padding:30px; color:#57606f; font-style:italic;">NO SIGNAL DETECTED</td></tr>"""

        st.markdown(f"""
<div class="metal-panel">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">ACTIVE TRANSMISSIONS</div>
<div class="black-screen" style="padding:0;">
<table class="trade-table">
<thead>
<tr style="background-color:#151515;">
<th>DIR</th><th>UNITS</th><th>INST</th><th>P/L</th><th>TSL</th><th>LOCK</th>
</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
</div>
</div>
""", unsafe_allow_html=True)

    time.sleep(2)
