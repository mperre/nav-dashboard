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
    st.error("Secrets not found! Please configure them in your hosting dashboard.")
    st.stop()

# ==========================================
# 2. VISUAL STYLING (The "Sci-Fi" Look)
# ==========================================
st.set_page_config(page_title="COMMAND INTERFACE", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

/* MAIN BACKGROUND */
.stApp {
    background-color: #000000;
}

/* REMOVE DEFAULT STREAMLIT PADDING */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 500px;
}

/* THE METAL PANEL CONTAINER */
.retro-panel {
    background-color: #1e272e;
    border: 4px solid #485460;
    border-radius: 15px;
    padding: 20px;
    position: relative;
    margin-bottom: 20px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}

/* FAKE SCREWS IN CORNERS */
.screw {
    position: absolute;
    width: 10px;
    height: 10px;
    background-color: #57606f;
    border-radius: 50%;
    border: 1px solid #2f3640;
}
.tl { top: 8px; left: 8px; }
.tr { top: 8px; right: 8px; }
.bl { bottom: 8px; left: 8px; }
.br { bottom: 8px; right: 8px; }

/* THE BLACK SCREEN INSERT */
.monitor-screen {
    background-color: #000000;
    border: 2px solid #2d3436;
    border-radius: 5px;
    padding: 40px 10px;
    text-align: center;
    margin-top: 10px;
    box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.05);
}

/* TEXT STYLES */
.panel-title {
    color: #808e9b;
    font-family: 'Orbitron', sans-serif;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 2px;
    margin-bottom: 5px;
    text-transform: uppercase;
}

.nav-value {
    font-family: 'Orbitron', sans-serif;
    color: #0be881;
    font-size: 60px;
    font-weight: 900;
    text-shadow: 0 0 10px rgba(11, 232, 129, 0.4);
}

/* CUSTOM TABLE FOR TRADES */
.trade-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Orbitron', sans-serif;
    font-size: 12px;
    color: #dcdde1;
    background-color: #000000;
}
.trade-table th {
    color: #808e9b;
    padding: 8px;
    border-bottom: 2px solid #485460;
    font-size: 10px;
}
.trade-table td {
    padding: 8px;
    text-align: center;
    border-bottom: 1px solid #2d3436;
}
.long { color: #0be881; }
.short { color: #ff3f34; }
.profit-yes { color: #0be881; font-weight: bold; }
.profit-wait { color: #ff9f43; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA ENGINE
# ==========================================
def get_data():
    base_url = "https://api-fxtrade.oanda.com/v3/accounts" if ENVIRONMENT == "live" else "https://api-fxpractice.oanda.com/v3/accounts"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    try:
        r1 = requests.get(f"{base_url}/{ACCOUNT_ID}/summary", headers=headers, timeout=5)
        r2 = requests.get(f"{base_url}/{ACCOUNT_ID}/openTrades", headers=headers, timeout=5)
        
        if r1.status_code == 200 and r2.status_code == 200:
            return r1.json()['account'], r2.json()['trades']
        else:
            return None, None
    except Exception as e:
        return None, None

# ==========================================
# 4. DRAWING THE INTERFACE
# ==========================================

placeholder = st.empty()

while True:
    acct, trades = get_data()
    
    with placeholder.container():
        # --- MODULE 1: NAV MONITOR ---
        nav_display = "---"
        if acct:
            nav_val = float(acct['NAV'])
            nav_display = f"£{nav_val:,.0f}"

        # Note: The HTML below is flush left to prevent Markdown errors
        st.markdown(f"""
<div class="retro-panel">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="panel-title">NAV MONITOR</div>
<div class="monitor-screen">
<div class="nav-value">{nav_display}</div>
</div>
</div>
""", unsafe_allow_html=True)

        # --- MODULE 2: ACTIVE TRANSMISSIONS ---
        rows_html = ""
        
        if trades:
            for t in trades:
                entry = float(t.get('price', 0))
                units = float(t['currentUnits'])
                current_pl = float(t['unrealizedPL'])
                
                direction = "LONG" if units > 0 else "SHORT"
                dir_class = "long" if units > 0 else "short"
                
                tsl_status = "WAIT"
                profit_class = "profit-wait"
                tsl_val = "-"
                
                if 'trailingStopLossOrder' in t:
                    tsl_trigger = t['trailingStopLossOrder'].get('triggerPrice')
                    if tsl_trigger:
                        trigger_price = float(tsl_trigger)
                        tsl_val = f"{trigger_price:.3f}"
                        if units > 0 and trigger_price > entry: 
                            tsl_status = "YES"
                            profit_class = "profit-yes"
                        elif units < 0 and trigger_price < entry: 
                            tsl_status = "YES"
                            profit_class = "profit-yes"

                pl_color = "#0be881" if current_pl >= 0 else "#ff9f43"

                rows_html += f"""
<tr>
<td class="{dir_class}">{direction}</td>
<td>{units}</td>
<td>{t['instrument']}</td>
<td style="color:{pl_color}">£{current_pl:.2f}</td>
<td>{tsl_val}</td>
<td class="{profit_class}">{tsl_status}</td>
</tr>"""
        else:
            rows_html = "<tr><td colspan='6' style='padding:20px; color:#57606f;'>NO SIGNAL DETECTED</td></tr>"

        st.markdown(f"""
<div class="retro-panel">
<div class="screw tl"></div><div class="screw tr"></div>
<div class="screw bl"></div><div class="screw br"></div>
<div class="panel-title">ACTIVE TRANSMISSIONS</div>
<div class="monitor-screen" style="padding: 0; overflow: hidden;">
<table class="trade-table">
<thead>
<tr>
<th>DIR</th>
<th>UNITS</th>
<th>INST</th>
<th>P/L</th>
<th>TSL</th>
<th>LOCK</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</div>
</div>
""", unsafe_allow_html=True)

    time.sleep(2)
