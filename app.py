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
    st.error("Secrets missing.")
    st.stop()

st.set_page_config(page_title="COMMAND INTERFACE", layout="wide")

# ==========================================
# 2. FULLSCREEN LAYOUT ENGINE (CSS)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* GLOBAL RESET - Force Full Height */
.stApp {
    background-color: #0d1117 !important;
    overflow: hidden; /* Lock scrollbar if possible for app feel */
}
.block-container {
    padding: 1rem 1rem !important;
    max-width: 600px !important;
    margin: 0 auto;
    height: 100vh; /* Fill the screen */
    display: flex;
    flex-direction: column;
}
header, footer {display: none !important;}

/* --- TOP PANEL (NAV) --- 
   This forces the top box to take 55% of the screen height 
*/
.nav-container {
    flex: 55; /* Takes 55% of available space */
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 8px;
    position: relative;
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
    padding: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.6);
}

/* The Black Screen inside the Top Panel - Fills remaining space */
.nav-screen {
    background-color: #000000;
    border: 2px solid #2d3436;
    flex-grow: 1; /* Stretch to fill the metal box */
    display: flex;
    align-items: center;     /* Vertical Center */
    justify-content: center; /* Horizontal Center */
    box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.05);
    margin-top: 5px;
}

/* --- BOTTOM PANEL (TRADES) ---
   This forces the bottom box to take 35% of the screen height
*/
.trade-container {
    flex: 35; /* Takes 35% of available space */
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 8px;
    position: relative;
    padding: 15px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 8px rgba(0,0,0,0.6);
}

.trade-screen {
    background-color: #000000;
    border: 2px solid #2d3436;
    flex-grow: 1; /* Stretch to fill */
    margin-top: 5px;
    overflow-y: auto; /* Allow scrolling only inside this small box if many trades */
}

/* SCREWS & DECORATION */
.screw {
    position: absolute;
    width: 8px;
    height: 8px;
    background-color: #57606f;
    border-radius: 50%;
    border: 1px solid #2f3640;
    z-index: 10;
}
.tl { top: 6px; left: 6px; }
.tr { top: 6px; right: 6px; }
.bl { bottom: 6px; left: 6px; }
.br { bottom: 6px; right: 6px; }

/* TEXT STYLES */
.label-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 12px;
    color: #808e9b;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.nav-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 15vw; /* Responsive font size based on width */
    color: #0be881;
    font-weight: 900;
    text-shadow: 0 0 20px rgba(11, 232, 129, 0.4);
    line-height: 1;
}
@media (min-width: 600px) { .nav-value { font-size: 80px; } }

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
    padding: 8px 2px;
    border-bottom: 1px solid #485460;
    position: sticky;
    top: 0;
    background: #000000;
}
.trade-table td {
    padding: 8px 2px;
    text-align: center;
    border-bottom: 1px solid #2d3436;
}

/* STATUS COLORS */
.long { color: #0be881; }
.short { color: #ff3f34; }
.profit-yes { color: #0be881; font-weight: bold; }
.profit-wait { color: #ff9f43; }

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
# 4. RENDER LOOP
# ==========================================
placeholder = st.empty()

while True:
    acct, trades = get_data()
    
    with placeholder.container():
        
        # --- PREPARE DATA ---
        nav_str = "---"
        if acct:
            nav_str = f"£{float(acct['NAV']):,.0f}"

        trade_rows = ""
        if trades:
            for t in trades:
                units = float(t['currentUnits'])
                entry = float(t.get('price', 0))
                pl = float(t['unrealizedPL'])
                
                side_cls = "long" if units > 0 else "short"
                side_txt = "LONG" if units > 0 else "SHORT"
                pl_col = "#0be881" if pl >= 0 else "#ff9f43"
                
                tsl_show = "-"
                lock_show = "WAIT"
                lock_cls = "profit-wait"
                
                if 'trailingStopLossOrder' in t:
                    trig = t['trailingStopLossOrder'].get('triggerPrice')
                    if trig:
                        t_val = float(trig)
                        tsl_show = f"{t_val:.3f}"
                        if (units > 0 and t_val > entry) or (units < 0 and t_val < entry):
                            lock_show = "LOCKED"
                            lock_cls = "profit-yes"

                trade_rows += f"""
                <tr>
                    <td class="{side_cls}">{side_txt}</td>
                    <td>{int(units)}</td>
                    <td>{t['instrument'].replace('_','/')}</td>
                    <td style="color:{pl_col}">£{pl:.2f}</td>
                    <td>{tsl_show}</td>
                    <td class="{lock_cls}">{lock_show}</td>
                </tr>"""
        else:
            trade_rows = "<tr><td colspan='6' style='padding:40px 0; color:#57606f;'>NO SIGNAL</td></tr>"

        # --- DRAW INTERFACE (Flush Left HTML) ---
        st.markdown(f"""
<div class="nav-container">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">NAV MONITOR</div>
<div class="nav-screen">
<div class="nav-value">{nav_str}</div>
</div>
</div>

<div class="trade-container">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="label-text">ACTIVE TRANSMISSIONS</div>
<div class="trade-screen">
<table class="trade-table">
<thead>
<tr><th>DIR</th><th>UNITS</th><th>INST</th><th>P/L</th><th>TSL</th><th>LOCK</th></tr>
</thead>
<tbody>
{trade_rows}
</tbody>
</table>
</div>
</div>
""", unsafe_allow_html=True)

    time.sleep(2)
