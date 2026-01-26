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
# 2. CSS STYLING
# ==========================================
if st.session_state.secure_mode:
    dash_opacity = "0"
    dash_pointer = "none"
    dash_transition = "opacity 0s" 
else:
    dash_opacity = "1"
    dash_pointer = "auto"
    dash_transition = "opacity 0.5s ease-in" 

css_template = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');

/* GLOBAL SETTINGS */
.stApp {{
    background-color: #000000 !important;
    overflow: hidden !important; 
}}

#MainMenu, footer, header {{visibility: hidden !important;}}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{display: none !important;}}

::-webkit-scrollbar {{ display: none; }}
* {{ -ms-overflow-style: none; scrollbar-width: none; }}

/* -----------------------------------------------------------
   CONFETTI IFRAME
----------------------------------------------------------- */
iframe {{
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: 2147483647 !important; 
    pointer-events: none !important; 
    background: transparent !important;
    border: none !important;
}}

/* FULL SCREEN INTERACTION BUTTON */
div.stButton > button {{
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: 999999 !important; /* Below confetti, Above dashboard */
    background-color: transparent !important;
    border: none !important;
    color: transparent !important;
    cursor: default !important; 
    border-radius: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}
div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {{
    background-color: transparent !important;
    border: none !important;
    color: transparent !important;
    box-shadow: none !important;
}}

/* DASHBOARD CONTAINER */
.block-container {{
    margin: 0 !important;
    margin-top: -55px !important; 
    padding: 27px 10px 0 10px !important;
    max-width: 100% !important;
    height: 100vh !important; 
    min-height: 100vh !important;
    overflow: hidden !important;
    display: flex;
    flex-direction: column;
}}

.dashboard-container {{
    height: calc(100vh - 74px);
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 15px; 
    box-sizing: border-box;
    opacity: {dash_opacity};
    pointer-events: {dash_pointer};
    transition: {dash_transition}; 
}}

/* COMPONENT BOXES */
.nav-box, .trade-box {{
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 10px;
    position: relative;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}}

/* Top box flexes to fill space */
.nav-box {{ flex: 1; min-height: 200px; }}
.trade-box {{ flex: 0 0 auto; max-height: 40vh; display: flex; flex-direction: column; }}

/* SCREEN & TEXT */
.screen {{
    background-color: #000000;
    border: 2px solid #2d3436;
    border-radius: 4px;
    box-shadow: inset 0 0 30px rgba(255,255,255,0.02);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    width: 100%;
    height: 100%;
}}
.label-text {{ font-family: 'Orbitron'; font-size: 12px; color: #808e9b; font-weight: 800; letter-spacing: 1px; margin-bottom: 8px; text-transform: uppercase; padding-left: 4px; }}
.nav-value {{ font-family: 'Orbitron'; color: #0be881; font-weight: 900; line-height: 1; margin-top: -10px; }}

/* TABLE */
.trade-table {{ width: 100%; color: #dcdde1; font-family: 'Orbitron'; font-size: 11px; border-collapse: collapse; }}
.trade-table th {{ border-bottom: 1px solid #485460; padding: 8px 2px; color: #808e9b; text-align: center; background: #050505; position: sticky; top: 0; }}
.trade-table td {{ border-bottom: 1px solid #2d3436; padding: 10px 2px; text-align: center; }}

/* SCREWS */
.screw {{ position: absolute; width: 6px; height: 6px; background: #57606f; border-radius: 50%; border: 1px solid #2f3640; z-index: 5; }}
.tl {{top:6px; left:6px;}} .tr {{top:6px; right:6px;}} .bl {{bottom:6px; left:6px;}} .br {{bottom:6px; right:6px;}}
</style>
"""
st.markdown(css_template, unsafe_allow_html=True)

# ==========================================
# 3. JAVASCRIPT INJECTION (CONFETTI)
# ==========================================
confetti_html = """
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
<script>
    const doc = window.parent.document;
    let touchStartX = 0;
    let touchStartY = 0;

    function shootConfetti() {
        try { window.navigator.vibrate(200); } catch(e) {}
        
        var duration = 3000;
        var animationEnd = Date.now() + duration;
        var defaults = { startVelocity: 45, spread: 360, ticks: 60, zIndex: 2147483647 };
        var randomInRange = (min, max) => Math.random() * (max - min) + min;

        var interval = setInterval(function() {
            var timeLeft = animationEnd - Date.now();
            if (timeLeft <= 0) { return clearInterval(interval); }
            var particleCount = 50 * (timeLeft / duration);
            confetti(Object.assign({}, defaults, { 
                particleCount, 
                origin: { x: randomInRange(0.1, 0.9), y: Math.random() - 0.2 } 
            }));
        }, 250);
        
        // BLAST
        confetti({
            particleCount: 150, spread: 120, origin: { y: 1 },
            colors: ['#0be881', '#ffffff', '#57606f'],
            startVelocity: 85, gravity: 0.8, scalar: 1.2, zIndex: 2147483647
        });
    }

    function onTouchStart(e) {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }

    function onTouchEnd(e) {
        let touchEndX = e.changedTouches[0].screenX;
        let touchEndY = e.changedTouches[0].screenY;
        let diffX = touchEndX - touchStartX;
        let diffY = touchEndY - touchStartY;

        // SWIPE THRESHOLD: > 30px horizontal
        if (Math.abs(diffX) > 30 && Math.abs(diffX) > Math.abs(diffY)) {
            shootConfetti();
        }
    }

    doc.addEventListener('touchstart', onTouchStart, true);
    doc.addEventListener('touchend', onTouchEnd, true);
</script>
"""
components.html(confetti_html, height=0)

# ==========================================
# 4. HAPTIC LOGIC
# ==========================================
if st.session_state.trigger_haptic:
    js_vibration = """<script>try { window.navigator.vibrate(50); } catch(e) {}</script>"""
    components.html(js_vibration, height=0)
    st.session_state.trigger_haptic = False

# ==========================================
# 5. TOGGLE BUTTON
# ==========================================
st.button(" ", on_click=toggle_secure, key="overlay_btn")

# ==========================================
# 6. DATA ENGINE
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
# 7. RENDER
# ==========================================
acct, trades = get_data()

nav_str = "£0" 
if acct: 
    nav_str = f"£{float(acct['NAV']):,.0f}"

char_len = len(nav_str)
if char_len <= 4: f_size = "min(25vh, 25vw)"
elif char_len <= 6: f_size = "min(19vh, 19vw)"
elif char_len <= 7: f_size = "min(15vh, 15vw)"
else: f_size = "min(12vh, 12vw)"

# --- CONDITIONAL COLUMNS CHECK ---
# Check if ANY trade has a Trailing Stop Loss
show_tsl_cols = False
if trades:
    for t in trades:
        if 'trailingStopLossOrder' in t and t['trailingStopLossOrder'].get('triggerPrice'):
            show_tsl_cols = True
            break
# ---------------------------------

rows = ""
if trades:
    for t in trades:
        u = float(t['currentUnits'])
        entry = float(t.get('price', 0))
        pl = float(t['unrealizedPL'])
        side = "LONG" if u > 0 else "SHORT"
        pl_color = "#0be881" if pl >= 0 else "#ff9f43"
        dir_color = "#0be881" if u > 0 else "#ff3f34"
        
        # Calculate TSL/LOCK values
        tsl, l_s, l_c = "-", "-", "#dcdde1"
        
        if 'trailingStopLossOrder' in t:
            trig = t['trailingStopLossOrder'].get('triggerPrice')
            if trig:
                tv = float(trig)
                tsl = f"{tv:.3f}"
                l_s, l_c = "WAIT", "#ff9f43"
                if (u > 0 and tv > entry) or (u < 0 and tv < entry):
                    l_s, l_c = "LOCKED", "#0be881"
        
        # Construct Row HTML
        extra_cells = ""
        if show_tsl_cols:
            extra_cells = f"<td>{tsl}</td><td style='color:{l_c}; font-weight:bold;'>{l_s}</td>"

        rows += f"""<tr>
            <td style="color: {dir_color}">{side}</td>
            <td>{int(u)}</td>
            <td>{t['instrument'].replace('_','/')}</td>
            <td style="color:{pl_color}">£{pl:.2f}</td>
            {extra_cells}
        </tr>"""
else:
    # Adjust colspan if TSL cols are hidden (4 cols vs 6 cols)
    col_span = "6" if show_tsl_cols else "4"
    rows = f"<tr><td colspan='{col_span}' style='padding:20px; color:#57606f; font-style:italic;'>NO SIGNAL DETECTED</td></tr>"

# Construct Header HTML
extra_headers = ""
if show_tsl_cols:
    extra_headers = "<th>TSL</th><th>LOCK</th>"

dashboard_html = f"""
<div class="dashboard-container">
    <div class="nav-box">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>
        <div class="label-text">NAV MONITOR</div>
        <div class="screen">
            <div class="nav-value" style="font-size: {f_size};">{nav_str}</div>
        </div>
    </div>
    <div class="trade-box">
        <div class="screw tl"></div><div class="screw tr"></div>
        <div class="screw bl"></div><div class="screw br"></div>
        <div class="label-text">ACTIVE TRANSMISSIONS</div>
        <div class="screen" style="display:block; padding:0; flex:1; min-height:0; overflow-y:auto;">
            <table class="trade-table">
                <thead>
                    <tr><th>DIR</th><th>UNITS</th><th>INST</th><th>P/L</th>{extra_headers}</tr>
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
