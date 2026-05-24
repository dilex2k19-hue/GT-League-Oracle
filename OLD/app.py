import streamlit as st
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="GT Validator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Main Background - WHITE */
    .stApp { background-color: #ffffff; color: #000000; }
    
    /* Input Boxes */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #f0f2f6; color: black; border-radius: 8px;
    }
    
    /* Stats Cards */
    .stats-card {
        background-color: #f8f9fa; padding: 20px; border-radius: 12px;
        border: 1px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    
    /* Verdict Card */
    .verdict-card {
        padding: 25px; border-radius: 15px; text-align: center;
        height: 100%; display: flex; flex-direction: column;
        justify-content: center; align-items: center; border: 2px solid #000;
    }
    
    /* Typography */
    .big-score { font-size: 24px; font-weight: bold; color: #333; }
    .sub-text { font-size: 14px; color: #666; }
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        with open("fetched_players.json", "r") as f:
            raw_data = json.load(f)
        return {p['nickname']: p for p in raw_data['data']}
    except FileNotFoundError:
        return None

players_db = load_data()

# --- HEADER ---
st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>⚡ GT VALIDATOR PRO</h1>", unsafe_allow_html=True)

# --- INPUT SECTION ---
if players_db:
    player_names = sorted(list(players_db.keys()))
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            p1_name = st.selectbox("Player 1 (Home)", player_names, index=None, placeholder="Select Home...")
        with col_input2:
            p2_name = st.selectbox("Player 2 (Away)", player_names, index=None, placeholder="Select Away...")

    st.markdown("---")

    # --- ANALYSIS ENGINE ---
    if p1_name and p2_name:
        p1 = players_db[p1_name]
        p2 = players_db[p2_name]

        def get_stats(p):
            gp = int(p['games_played'])
            if gp == 0: return 0.0, 0.0, 0.0
            gf_avg = float(p['goals_total_for']) / gp
            ga_avg = float(p['goals_total_against']) / gp
            total_avg = gf_avg + ga_avg
            return gf_avg, ga_avg, total_avg

        p1_gf, p1_ga, p1_total = get_stats(p1)
        p2_gf, p2_ga, p2_total = get_stats(p2)
        
        # --- NEW CORE LOGIC: MATCH EXPECTED GOALS ---
        # This is the average of both players' total activity.
        # Example: P1 (3.5) + P2 (4.5) = 8.0 / 2 = 4.0 Expected Goals
        match_expected_goals = (p1_total + p2_total) / 2

        # --- DECISION MATRIX ---
        verdict_title = "⚠️ SKIP / NO BET"
        verdict_color = "#fff3e0" # Default Orange
        verdict_border = "#ffe0b2"
        verdict_icon = "✋"
        verdict_msg = "Match is unpredictable."

        # STRATEGY 1: UNDER 5.5 (Defensive Lock)
        # Condition: Expected goals <= 3.8
        if match_expected_goals <= 3.8:
            verdict_title = "🛡️ BET UNDER 5.5"
            verdict_color = "#e3f2fd" # Light Blue
            verdict_border = "#2196f3" # Blue Border
            verdict_icon = "❄️"
            verdict_msg = "Defensive game expected. High safety margin."

        # STRATEGY 2: OVER 1.5 (High Volatility)
        # Condition: Expected goals >= 3.25 AND NOT a Defensive Lock
        # Note: If it's chaotic (e.g., > 4.5), it's even better.
        elif match_expected_goals >= 3.25:
            verdict_title = "✅ BET OVER 1.5"
            verdict_color = "#e8f5e9" # Light Green
            verdict_border = "#4caf50" # Green Border
            verdict_icon = "🔥"
            if match_expected_goals > 4.2:
                verdict_msg = "GOLD MINE! Extremely high goal expectancy."
                verdict_icon = "💰"
            else:
                verdict_msg = "Standard Volatility. Safe for Over 1.5."

        # --- LAYOUT: LEFT (Stats) | RIGHT (Verdict) ---
        left_col, right_col = st.columns([1.5, 1])

        with left_col:
            st.markdown("### 📊 Player Stats")
            
            # P1 Card
            st.markdown(f"""
            <div class="stats-card">
                <h3>🏠 {p1_name}</h3>
                <span class="sub-text">Scoring:</span> <span class="big-score" style="color:#2e7d32;">{p1_gf:.2f}</span>
                &nbsp;|&nbsp;
                <span class="sub-text">Conceding:</span> <span class="big-score" style="color:#c62828;">{p1_ga:.2f}</span>
                <br><b>Activity Avg: {p1_total:.2f}</b>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='text-align:center; font-weight:bold; color:#999;'>VS</div>", unsafe_allow_html=True)

            # P2 Card
            st.markdown(f"""
            <div class="stats-card">
                <h3>✈️ {p2_name}</h3>
                <span class="sub-text">Scoring:</span> <span class="big-score" style="color:#2e7d32;">{p2_gf:.2f}</span>
                &nbsp;|&nbsp;
                <span class="sub-text">Conceding:</span> <span class="big-score" style="color:#c62828;">{p2_ga:.2f}</span>
                <br><b>Activity Avg: {p2_total:.2f}</b>
            </div>
            """, unsafe_allow_html=True)

        with right_col:
            st.markdown("### 🤖 Strategy")
            
            st.markdown(f"""
            <div class="verdict-card" style="background-color: {verdict_color}; border: 3px solid {verdict_border};">
                <div style="font-size: 60px;">{verdict_icon}</div>
                <h2 style="margin: 10px 0; font-size: 28px;">{verdict_title}</h2>
                <p style="font-size: 16px; color: #444; font-weight: bold;">{verdict_msg}</p>
                <hr style="width: 80%; border-top: 1px solid #999;">
                <p><b>Expected Goals:</b></p>
                <div style="font-size: 40px; font-weight: bold;">{match_expected_goals:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.error("Fetched players data not found. Please run the scraper.")
