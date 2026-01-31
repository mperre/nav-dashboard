import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import base64

# ==========================================
# 0. SOUND ASSET (Base64 Encoded "Ka-Ching")
# ==========================================
CASH_REGISTER_MP3 = """
SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4LjI5LjEwMAAAAAAAAAAAAAAA//uQZA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWgAAAA0AAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAATGF2YzU4LjU0AAAAAAAAAAAAAAAAJAAAAAAAAAAAAScc8T+4AAA
AAAAAAAAAAAAAAAAAAAP/7kmRAABfdozL0wAAR+TRmXpgAAxp1WfMvAAADLqs+ZeAA
AEFuaM7qO/M5/0f/R//R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R
/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9
H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/
0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f/R/9H/0f
"""

# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(page_title="COMMAND INTERFACE", layout="wide")

if 'secure_mode' not in st.session_state:
    st.session_state.secure_mode = False

if 'trigger_haptic' not in st.session_state:
    st.session_state.trigger_haptic = False

if 'known_trades' not in st.session_state:
    st.session_state.known_trades = set()

if 'first_run' not in st.session_state:
    st.session_state.first_run = True

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
        # Default credentials
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

# --- DYNAMIC TABLE SIZING ---
# Determines font size and padding based on number of active trades
t_count = len(trades) if trades else 0

if t_count > 12:
    t_font = "9px"
    t_pad = "4px"
elif t_count > 7:
    t_font = "10px"
    t_pad = "6px"
else:
    # Default comfortable sizing
    t_font = "11px"
    t_pad = "10px"

# ==========================================
# 3. SOUND LOGIC
# ==========================================
if trades is not None:
    current_trade_ids = {t['id'] for t in trades}
    
    if not st.session_state.first_run:
        new_trades = current_trade_ids - st.session_state.known_trades
        if new_trades:
            sound_html = f"""
            <audio autoplay="true" style="display:none;">
                <source src="data:audio/mp3;base64,{CASH_REGISTER_MP3}" type="audio/mp3">
            </audio>
            """
            st.markdown(sound_html, unsafe_allow_html=True)
            
    else:
        st.session_state.first_run = False

    st.session_state.known_trades = current_trade_ids


# --- MARGIN LOGIC ---
real_margin_pct = 0.0
visual_width = 0.0
margin_color = "#0be881" # Default Green

if acct:
    nav_float = float(acct.get('NAV', 1))
    margin_used = float(acct.get('marginUsed', 0))
    if nav_float > 0:
        real_margin_pct = (margin_used / nav_float) * 100
    
    # Scale: 0% -> 0%, 50% -> 100%
    visual_width = (real_margin_pct / 50) * 100
    if visual_width > 100: visual_width = 100
    
    if real_margin_pct > 30: margin_color = "#ff9f43" 
    if real_margin_pct > 45: margin_color = "#ff3f34" 

# ==========================================
# 4. CSS STYLING
# ==========================================
dash_opacity = "0" if st.session_state.secure_mode else "1"
dash_pointer = "none" if st.session_state.secure_mode else "auto"

css_template = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

.stApp {{ background-color: #000000 !important; overflow: hidden !important; }}
#MainMenu, footer, header {{visibility: hidden !important;}}
[data-testid="stToolbar"] {{display: none !important;}}

/* --- INVISIBLE FULL-SCREEN TOGGLE BUTTON --- */
div.stButton > button:first-child {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: transparent !important;
    border: none !important;
    z-index: 99999 !important;
    color: transparent !important;
    opacity: 0 !important;
    cursor: default !important;
}}
/* Remove interactions on hover/focus to keep it invisible */
div.stButton > button:hover {{ background: transparent !important; }}
div.stButton > button:focus {{ background: transparent !important; box-shadow: none !important; }}
div.stButton > button:active {{ background: transparent !important; }}

/* Reset Streamlit default padding */
.block-container {{
    margin-top: -55px !important; 
    /* TOP: 45px (Border) | BOTTOM: 65px (Clear Icon) */
    padding: 45px 10px 65px 10px !important;
    max-width: 100% !important;
    height: 100vh !important;
    display: flex;
    flex-direction: column;
}}

/* FLEX CONTAINER */
.dashboard-container {{
    opacity: {dash_opacity};
    pointer-events: {dash_pointer};
    display: flex;
    flex-direction: column;
    gap: 12px;
    height: calc(100vh - 110px); /* 45 Top + 65 Bottom = 110px Reduction */
}}

.nav-box, .trade-box {{
    background-color: #1e272e;
    border: 3px solid #485460;
    border-radius: 6px;
    padding: 10px;
    position: relative;
    display: flex;
    flex-direction: column;
}}

/* --- DYNAMIC SIZING --- */
.nav-box {{ 
    flex: 1 1 auto; /* FLEX GROW to fill empty space */
    min-height: 140px; 
}}

.margin-box-wrapper {{
    flex: 0 0 auto;
    padding: 0 5px;
}}

.trade-box {{ 
    flex: 0 0 auto; /* PREVENT SHRINKING */
    max-height: 65vh; 
    overflow: hidden;
}}

/* --- INTERNAL GRAPHICS --- */
.margin-container {{
    position: relative;
    width: 100%;
    height: 32px;
    background: #000000;
    border: 1px solid #485460;
    border-radius: 3px;
    overflow: hidden;
    margin-top: 5px;
}}

.margin-text {{
    position: absolute;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 14px;
    letter-spacing: 1px;
    color: {margin_color};
    z-index: 1;
}}

.progress-bar {{
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: {visual_width}%;
    background-color: {margin_color};
    z-index: 2;
    mix-blend-mode: difference; 
    transition: width 0.5s ease-in-out;
}}

.screen {{
    background: #000;
    border: 2px solid #2d3436;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden; 
    position: relative;
}}

.nav-value {{ font-family: 'Orbitron', sans-serif; color: #0be881; font-weight: 700; }}

.digit-box {{ 
    display: inline-block; 
    width: 0.76em; 
    text-align: center; 
    margin: 0 1px; 
}}

/* --- DYNAMIC TRADE TABLE STYLES --- */
.trade-table {{ 
    width: 100%; 
    color: #dcdde1; 
    font-family: 'Orbitron', sans-serif; 
    font-size: {t_font}; /* DYNAMIC FONT */
    border-collapse: collapse; 
}}
.trade-table th {{ 
    border-bottom: 1px solid #485460; 
    padding: 8px; 
    color: #808e9b; 
    background: #050505; 
    position: sticky; 
    top: 0; 
    z-index: 10; 
    text-align: center; /* CENTERED HEADINGS */
}}
.trade-table td {{ 
    border-bottom: 1px solid #2d3436; 
    padding: {t_pad}; /* DYNAMIC PADDING */
    text-align: center; 
}}

.screw {{ position: absolute; width: 6px; height: 6px; background: #57606f; border-radius: 50%; }}
.tl {{top:6px; left:6px;}} .tr {{top:6px; right:6px;}} .bl {{bottom:6px; left:6px;}} .br {{bottom:6px; right:6px;}}
</style>
"""
st.markdown(css_template, unsafe_allow_html=True)

# ==========================================
# 5. RENDER
# ==========================================
st.button(" ", on_click=toggle_secure, key="overlay_btn")

val_str = f"{float(acct['NAV']):.0f}" if acct else "0"
char_len = len(val_str) + 1
# REVERTED TO LARGE SCALING AS BOX IS BIG AGAIN
f_size = "min(20vh, 20vw)" if char_len < 6 else "min(15vh, 15vw)"

nav_html = f'<span style="font-size:50%">£</span>' + "".join([f'<span class="digit-box">{c}</span>' for c in val_str])

rows = ""
if trades:
    for t in trades:
        u, pl = float(t['currentUnits']), float(t['unrealizedPL'])
        side = "LONG" if u > 0 else "SHORT"
        pl_c = "#0be881" if pl >= 0 else "#ff9f43"
        rows += f"<tr><td>{side}</td><td>{u}</td><td>{t['instrument']}</td><td style='color:{pl_c}'>£{pl:.2f}</td></tr>"
else:
    rows = "<tr><td colspan='4' style='padding:20px; color:#57606f; font-style:italic;'>NO ACTIVE TRADES</td></tr>"

dashboard_html = f"""
<div class="dashboard-container">

<div class="nav-box">
<div class="screw tl"></div><div class="screw tr"></div><div class="screw bl"></div><div class="screw br"></div>
<div style="font-family:'Orbitron'; color:#808e9b; font-size:12px; margin-bottom:5px;">NAV MONITOR</div>
<div class="screen">
<div class="nav-value" style="font-size:{f_size}">{nav_html}</div>
</div>
</div>

<div class="margin-box-wrapper">
<div style="font-family:'Orbitron'; color:#808e9b; font-size:12px;">MARGIN LOAD</div>
<div class="margin-container">
<div class="margin-text">{real_margin_pct:.1f}%</div>
<div class="progress-bar"></div>
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
