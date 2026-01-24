import streamlit as st
import requests
import time

# ==========================================
# 1. CONFIGURATION
# ==========================================
try:
    ACCOUNT_ID = st.secrets["ACCOUNT_ID"]
    API_TOKEN = st.secrets["API_TOKEN"]
    ENVIRONMENT = st.secrets["ENVIRONMENT"]
except FileNotFoundError:
    st.error("Secrets missing. Check Streamlit settings.")
    st.stop()

st.set_page_config(page_title="COMMAND INTERFACE", layout="centered")

# ==========================================
# 2. EXACT STYLE MATCH (CSS)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* BACKGROUND & GLOBAL */
.stApp {
    background-color: #000000 !important;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 5rem;
    max-width: 450px;
}
header {visibility: hidden;}

/* METAL PANEL CONTAINER */
.metal-panel {
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 8px;
    padding: 15px;
    position: relative;
    margin-bottom: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.6);
}

/* SCREWS */
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

/* BLACK SCREEN INSET */
.black-screen {
    background-color: #000000;
    border: 2px solid #2d3436;
    margin-top: 5px;
    padding: 10px;
    text-align: center;
    box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.05);
}

/* TYPOGRAPHY */
.label-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 12px;
    color: #808e9b;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 2px;
    text-shadow: 0px 1px 2px rgba(0,0,0,0.8);
}

.nav-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 55px;
    color: #0be881;
    font-weight: 900;
    text-shadow: 0 0 15px rgba(11, 232, 129, 0.3);
    margin: 15px 0;
}

/* TABLE STYLING */
.trade-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    color: #dcdde1;
}
.trade-table th {
    color: #808e9b;
    padding: 8px 4px;
    border-bottom: 1px solid #485460;
    font-weight: bold;
    text-align: center;
}
.trade-table td {
    padding: 10px 4px;
    text-align: center;
    border-bottom: 1px solid #2d3436;
}
/* STATUS COLORS */
.long { color: #0be881; }
.short { color: #ff3f34; }
.profit-yes { color: #0be881; font-weight: bold; text-shadow: 0 0 5px #0be881; }
.profit-wait { color: #ff9f43; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA LOGIC
# ==========================================
def get_oanda_data():
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
# 4. DRAW UI
# ==========================================
placeholder = st.empty()

while True:
    acct, trades = get_oanda_data()
    
    with placeholder.container():
        # --- NAV PANEL ---
        nav_display = "---"
        if acct:
            nav_display = f"£{float(acct['NAV']):,.0f}"
            
        st.markdown(f"""
<div class="metal-panel">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">NAV MONITOR</div>
<div class="black-screen">
<div class="nav-text">{nav_display}</div>
</div>
</div>
""", unsafe_allow_html=True)

        # --- TRADES PANEL ---
        table_rows = ""
        if trades:
            for t in trades:
                # Extract Data
                units = float(t['currentUnits'])
                entry = float(t.get('price', 0))
                pl = float(t['unrealizedPL'])
                
                # Logic
                side = "LONG" if units > 0 else "SHORT"
                side_cls = "long" if units > 0 else "short"
                pl_col = "#0be881" if pl >= 0 else "#ff9f43"
                
                # TSL & Lock Logic
                tsl_show = "-"
                lock_status = "WAIT"
                lock_cls = "profit-wait"
                
                if 'trailingStopLossOrder' in t:
                    trigger = t['trailingStopLossOrder'].get('triggerPrice')
                    if trigger:
                        trig_val = float(trigger)
                        tsl_show = f"{trig_val:.3f}"
                        # Check if profit locked
                        if (units > 0 and trig_val > entry) or (units < 0 and trig_val < entry):
                            lock_status = "LOCKED"
                            lock_cls = "profit-yes"

                table_rows += f"""
                <tr>
                    <td class="{side_cls}">{side}</td>
                    <td>{int(units)}</td>
                    <td>{t['instrument'].replace('_','/')}</td>
                    <td style="color:{pl_col}">£{pl:.2f}</td>
                    <td>{tsl_show}</td>
                    <td class="{lock_cls}">{lock_status}</td>
                </tr>
                """
        else:
            table_rows = """
            <tr><td colspan="6" style="padding:25px; color:#57606f; font-style:italic;">
            NO SIGNAL DETECTED
            </td></tr>
            """

        st.markdown(f"""
<div class="metal-panel">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">ACTIVE TRANSMISSIONS</div>
<div class="black-screen" style="padding: 0;">
<table class="trade-table">
<thead>
<tr style="background-color: #151515;">
<th>DIR</th> <th>UNITS</th> <th>INST</th> <th>P/L</th> <th>TSL</th> <th>LOCK</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>
</div>
</div>
""", unsafe_allow_html=True)

    time.sleep(2)
