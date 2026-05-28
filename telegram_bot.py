import requests
import psycopg2
import psycopg2.extras
import pandas as pd
import joblib
from datetime import datetime, timezone, timedelta
import time
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning)
import feature_calculators as fc

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_TOKEN = "8914691037:AAEldTQrOgtjEBk2vl-_RV-dBj6sJcSBU2U"
CHAT_ID = "7678532101"              # Your primary goals channel ID
WINNERS_CHAT_ID = "-1003320870164"  # Your private match winners channel ID

# --- TIMEZONE SETUP (CAT is UTC+2) ---
CAT_TZ = timezone(timedelta(hours=2))

# ---------------------------------------------------------
# 1. INITIALIZATION & DATABASE
# ---------------------------------------------------------
print("🧠 Waking up the Autonomous Telegram Oracle...")
scaler = joblib.load('models/scaler.pkl')
home_model = joblib.load('models/rf_home_model.pkl')
away_model = joblib.load('models/rf_away_model.pkl')
over25_model = joblib.load('models/rf_over25_model.pkl')


def get_db_connection():
    """Connects to Cloud DB if on GitHub, otherwise uses local DB."""
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    else:
        return psycopg2.connect(dbname="gt_league_db", user="postgres", password="admin123", host="localhost")
        
def setup_database():
    """Ensures the predictions memory table exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            home_player VARCHAR(50),
            away_player VARCHAR(50),
            kickoff_utc TIMESTAMP,
            prediction VARCHAR(50),
            confidence FLOAT,
            status VARCHAR(20) DEFAULT 'Pending'
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# ---------------------------------------------------------
# 2. TELEGRAM BROADCASTER
# ---------------------------------------------------------
def send_telegram_message(target_chat_id, message):
    """Sends a formatted message to a dynamically specified channel destination."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")

# ---------------------------------------------------------
# 3. THE FEEDBACK LOOP (RESULT CHECKER)
# ---------------------------------------------------------
def grade_past_predictions():
    """Checks if our past predictions won or lost."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get all pending predictions from the past 24 hours
    # Only select pending matches that kicked off more than 45 minutes ago
    # This prevents the bot from mixing up games currently being played
    shield_time = datetime.now(timezone.utc) - timedelta(minutes=45)
    
    cursor.execute(
        "SELECT * FROM predictions WHERE status = 'Pending' AND kickoff_utc <= %s ORDER BY kickoff_utc ASC;",
        (shield_time,)
    )
    pending = cursor.fetchall()
    
    if not pending:
        cursor.close()
        conn.close()
        return

    print("🔍 Checking results of past predictions...")
    
    # Pull finished matches from GT Leagues API
    now_utc = datetime.now(timezone.utc)
    start_of_day = now_utc - timedelta(days=1)
    time_str = f"between:{start_of_day.strftime('%Y-%m-%dT%H:%M:%S.000Z')},{now_utc.strftime('%Y-%m-%dT%H:%M:%S.999Z')}"
    
    url = "https://api.gtleagues.com/api/sports/6/fixtures"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://www.gtleagues.com",
        "Referer": "https://www.gtleagues.com/"
    }
    params = {"kickoff": time_str, "limit": 1000, "status": "in:3"} # 3 = Finished
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return
        
    finished_matches = response.json()
    
    results_message = "📊 <b>ORACLE RESULT UPDATE</b> 📊\n\n"
    updates_found = False
    
    for p in pending:
        for m in finished_matches:
            h_player = m['participants'][0]['participant']['player']['nickname']
            a_player = m['participants'][1]['participant']['player']['nickname']
            
            # 1. Extract and format the API match time safely
            try:
                m_time = datetime.strptime(m['kickoff'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=None)
                db_time = p['kickoff_utc'].replace(tzinfo=None)
            except Exception:
                continue
            
            # 2. Time-Lock: Check Names AND ensure kickoff is within a 15-minute window
            time_difference = abs((db_time - m_time).total_seconds())
            max_drift_seconds = 15 * 60 # 15 minutes
            
            if p['home_player'] == h_player and p['away_player'] == a_player and time_difference <= max_drift_seconds:
                h_score = m['result']['stats']['home_score']
                a_score = m['result']['stats']['away_score']
                total_goals = h_score + a_score
                
                # Grade the prediction
                won = False
                if p['prediction'] == 'Home Win' and h_score > a_score: won = True
                elif p['prediction'] == 'Away Win' and a_score > h_score: won = True
                elif p['prediction'] == 'Over 2.5' and total_goals > 2: won = True
                
                new_status = "Won" if won else "Lost"
                icon = "✅" if won else "❌"
                
                # Update Database
                cursor.execute("UPDATE predictions SET status = %s WHERE id = %s", (new_status, p['id']))
                conn.commit()
                
                # Convert the database UTC time back to CAT for the message
                db_utc = p['kickoff_utc']
                if db_utc.tzinfo is None:
                    db_utc = db_utc.replace(tzinfo=timezone.utc)
                kickoff_cat = db_utc.astimezone(CAT_TZ).strftime("%H:%M CAT")
                
                results_message += f"{icon} <b>{p['prediction']}</b> ({p['home_player']} vs {p['away_player']})\n"
                results_message += f"⏰ Match Time: {kickoff_cat}\n"
                results_message += f"Score: {h_score} - {a_score}\n\n"
                updates_found = True
                break

    cursor.close()
    conn.close()
    
    if updates_found:
        send_telegram_message(CHAT_ID, results_message)

# ---------------------------------------------------------
# 4. DATA FETCHING & AI PREDICTION
# ---------------------------------------------------------
def fetch_history(player_name, cursor, is_home_player):
    cursor.execute("""
        SELECT * FROM matches 
        WHERE home_player = %s OR away_player = %s 
        ORDER BY timestamp ASC
    """, (player_name, player_name))
    matches = cursor.fetchall()
    history = {"all": [], "side": []}
    
    for match in matches:
        is_home = match['home_player'] == player_name
        result = {
            "result": "W" if (is_home and match['winner'] == 'Home') or (not is_home and match['winner'] == 'Away') else "L" if match['winner'] != 'Draw' else "D",
            "scored": match['home_goals'] if is_home else match['away_goals'],
            "conceded": match['away_goals'] if is_home else match['home_goals'],
            "over25": match['over25'],
            "timestamp": match['timestamp']
        }
        history["all"].append(result)
        if is_home == is_home_player: history["side"].append(result)
    return history

def fetch_h2h_history(home_player, away_player, cursor):
    cursor.execute("""
        SELECT * FROM matches 
        WHERE (home_player = %s AND away_player = %s) 
           OR (home_player = %s AND away_player = %s)
        ORDER BY timestamp ASC
    """, (home_player, away_player, away_player, home_player))
    return cursor.fetchall()

def get_predictions(home_player, away_player):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    home_hist = fetch_history(home_player, cursor, True)
    away_hist = fetch_history(away_player, cursor, False)
    
    cursor.execute("""
        SELECT * FROM matches 
        WHERE (home_player = %s AND away_player = %s) OR (home_player = %s AND away_player = %s)
        ORDER BY timestamp ASC
    """, (home_player, away_player, away_player, home_player))
    raw_h2h = cursor.fetchall()
    h2h_hist = [{"winner": m['winner'], "total_goals": m['home_goals'] + m['away_goals'], "over25": m['over25']} for m in raw_h2h]
    
    cursor.close()
    conn.close()
    
    if not home_hist["all"] or not away_hist["all"]: return None

    now = datetime.now()
    
    # Calculate Features
    h_roll = fc.calc_rolling_stats(home_hist["all"])
    h_strk = fc.calc_streaks(home_hist["all"])
    h_side = fc.calc_rolling_stats(home_hist["side"])
    h_cons = fc.calc_consistency_stats(home_hist["all"])
    h_vol = fc.calc_volume(home_hist["all"], now)
    
    a_roll = fc.calc_rolling_stats(away_hist["all"])
    a_strk = fc.calc_streaks(away_hist["all"])
    a_side = fc.calc_rolling_stats(away_hist["side"])
    a_cons = fc.calc_consistency_stats(away_hist["all"])
    a_vol = fc.calc_volume(away_hist["all"], now)
    
    h2h_all = fc.calc_h2h_stats(h2h_hist, home_player, away_player)
    h2h_l5 = fc.calc_recent_h2h_stats(h2h_hist, home_player, away_player)

    snapshot = {
        "match_hour": now.hour,
        "home_win_rate_l10": h_roll["win_rate_l10"], "home_draw_rate_l10": h_roll["draw_rate_l10"], "home_loss_rate_l10": h_roll["loss_rate_l10"],
        "home_avg_goals_l10": h_roll["avg_goals_l10"], "home_avg_conceded_l10": h_roll["avg_conceded_l10"], "home_over25_rate_l10": h_roll["over25_rate_l10"],
        "home_matches_seen_l10": h_roll["matches_seen_l10"], "home_win_streak_current": h_strk["win_streak_current"], "home_over_streak_current": h_strk["over_streak_current"],
        "home_scored_in_l5_rate": h_cons["scored_in_l5_rate"], "home_clean_sheet_rate_l10": h_cons["clean_sheet_rate_l10"], "home_win_rate_side_l10": h_side["win_rate_l10"],
        "home_avg_goals_side_l10": h_side["avg_goals_l10"], "home_side_matches_seen": h_side["matches_seen_l10"], "home_daily_matches_played": h_vol["daily_matches_played"],
        "home_matches_last_24h": h_vol["matches_last_24h"], "home_matches_last_7d": h_vol["matches_last_7d"],
        "away_win_rate_l10": a_roll["win_rate_l10"], "away_draw_rate_l10": a_roll["draw_rate_l10"], "away_loss_rate_l10": a_roll["loss_rate_l10"],
        "away_avg_goals_l10": a_roll["avg_goals_l10"], "away_avg_conceded_l10": a_roll["avg_conceded_l10"], "away_over25_rate_l10": a_roll["over25_rate_l10"],
        "away_matches_seen_l10": a_roll["matches_seen_l10"], "away_win_streak_current": a_strk["win_streak_current"], "away_over_streak_current": a_strk["over_streak_current"],
        "away_scored_in_l5_rate": a_cons["scored_in_l5_rate"], "away_clean_sheet_rate_l10": a_cons["clean_sheet_rate_l10"], "away_win_rate_side_l10": a_side["win_rate_l10"],
        "away_avg_goals_side_l10": a_side["avg_goals_l10"], "away_side_matches_seen": a_side["matches_seen_l10"], "away_daily_matches_played": a_vol["daily_matches_played"],
        "away_matches_last_24h": a_vol["matches_last_24h"], "away_matches_last_7d": a_vol["matches_last_7d"],
        "h2h_matches_played": h2h_all["h2h_matches_played"], "h2h_home_wins": h2h_all["h2h_home_wins"], "h2h_away_wins": h2h_all["h2h_away_wins"],
        "h2h_draws": h2h_all["h2h_draws"], "h2h_avg_goals": h2h_all["h2h_avg_goals"], "h2h_over25_rate": h2h_all["h2h_over25_rate"],
        "h2h_l5_played": h2h_l5["h2h_l5_played"], "h2h_l5_home_wins": h2h_l5["h2h_l5_home_wins"], "h2h_l5_away_wins": h2h_l5["h2h_l5_away_wins"],
        "h2h_l5_draws": h2h_l5["h2h_l5_draws"], "h2h_l5_avg_goals": h2h_l5["h2h_l5_avg_goals"], "h2h_l5_over25_rate": h2h_l5["h2h_l5_over25_rate"],
        "win_rate_diff": round(h_roll["win_rate_l10"] - a_roll["win_rate_l10"], 4), "avg_goals_diff": round(h_roll["avg_goals_l10"] - a_roll["avg_goals_l10"], 4),
        "over25_rate_diff": round(h_roll["over25_rate_l10"] - a_roll["over25_rate_l10"], 4), "home_weighted_winrate": 0.0, "away_weighted_winrate": 0.0
    }
    
    df = pd.DataFrame([snapshot])
    expected_features = scaler.feature_names_in_
    for col in expected_features:
        if col not in df.columns: df[col] = 0.0
    df = df[expected_features]
    
    X_scaled = scaler.transform(df)
    
    return {
        "Home Win": float(round(home_model.predict_proba(X_scaled)[0][1] * 100, 1)),
        "Away Win": float(round(away_model.predict_proba(X_scaled)[0][1] * 100, 1)),
        "Over 2.5": float(round(over25_model.predict_proba(X_scaled)[0][1] * 100, 1))
    }

# ---------------------------------------------------------
# 5. THE LIVE PIPELINE
# ---------------------------------------------------------
def run_pipeline():
    setup_database()
    grade_past_predictions() # Step 1: Grade the past
    
    # --- ANTI-SPAM FILTER MEMORY ---
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT home_player, away_player, prediction FROM predictions WHERE status = 'Pending';")
    pending_setups = {(row['home_player'], row['away_player'], row['prediction']) for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    
    print("📡 Scanning GT Leagues for setups strictly in the next 45 minutes...")
    now_utc = datetime.now(timezone.utc)
    start_of_day = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    time_str = f"between:{start_of_day.strftime('%Y-%m-%dT%H:%M:%S.000Z')},{end_of_day.strftime('%Y-%m-%dT%H:%M:%S.999Z')}"
    
    url = "https://api.gtleagues.com/api/sports/6/fixtures"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://www.gtleagues.com",
        "Referer": "https://www.gtleagues.com/"
    }
    params = {"kickoff": time_str, "limit": 1000, "offset": 0, "status": "in:1,0"}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200: 
        print(f"❌ API Blocked us! Status Code: {response.status_code}")
        return
    
    data = response.json()
    
    # --- THE GATEKEEPER: STRICT 45-MINUTE WINDOW ---
    target_window = now_utc + timedelta(minutes=45) 
    
    analyzed_matches = []
    
    for match in data:
        if match.get('status') == 0:
            kickoff_utc = datetime.strptime(match['kickoff'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            
            # If the match is not happening in the next 45 mins, ignore it completely
            if now_utc <= kickoff_utc <= target_window:
                home_player = match['participants'][0]['participant']['player']['nickname']
                away_player = match['participants'][1]['participant']['player']['nickname']
                
                probs = get_predictions(home_player, away_player)
                if probs:
                    # Find the absolute best mathematical edge for this specific match
                    best_pick = max(probs, key=probs.get)
                    confidence = probs[best_pick]
                    
                    kickoff_cat = kickoff_utc.astimezone(CAT_TZ).strftime("%H:%M CAT")
                    
                    analyzed_matches.append({
                        "home": home_player, "away": away_player,
                        "kickoff_utc": kickoff_utc, "kickoff_cat": kickoff_cat,
                        "best_pick": best_pick, "confidence": confidence
                    })

    if not analyzed_matches:
        print("⚠️ No matches found in the immediate 45-minute window.")
        return
        
    # --- SORTING ENGINE: TAKE TOP 2 ONLY ---
    analyzed_matches.sort(key=lambda x: x['confidence'], reverse=True)
    top_picks = analyzed_matches[:2]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for match in top_picks:
        h_player = match['home']
        a_player = match['away']
        best_pick = match['best_pick']
        conf = match['confidence']
        k_utc = match['kickoff_utc']
        k_cat = match['kickoff_cat']
        
        # Skip if we already sent this exact signal earlier
        if (h_player, a_player, best_pick) in pending_setups:
            continue
            
        # --- MULTI-CHANNEL ROUTER LOGIC ---
        if best_pick == "Over 2.5":
            msg = (
                "🏆 <b>ELITE GOAL PREDICTION FOUND</b> 🏆\n\n"
                f"🔥 <b>PICK:</b> {h_player} vs {a_player}\n"
                f"⏰ <b>Time:</b> {k_cat}\n"
                f"🎯 <b>Prediction:</b> <u>Over 2.5</u> ({conf} %)\n"
            )
            print(f"📲 Pushing Goals Signal: {h_player} vs {a_player} to Channel 1")
            send_telegram_message(CHAT_ID, msg)
        else:
            # Route Home Win / Away Win to the Private Winners Channel
            msg = (
                "👑 <b>ELITE MATCH WINNER SIGNAL</b> 👑\n\n"
                f"🔥 <b>PICK:</b> {h_player} vs {a_player}\n"
                f"⏰ <b>Time:</b> {k_cat}\n"
                f"🎯 <b>Prediction:</b> <u>{best_pick}</u> ({conf} %)\n"
            )
            print(f"📲 Pushing Winner Signal: {h_player} vs {a_player} to Channel 2")
            send_telegram_message(WINNERS_CHAT_ID, msg)
            
        # Log to Database Memory
        cursor.execute("""
            INSERT INTO predictions (home_player, away_player, kickoff_utc, prediction, confidence)
            VALUES (%s, %s, %s, %s, %s)
        """, (h_player, a_player, k_utc, best_pick, conf))
        conn.commit()
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("🚀 GT League Oracle Bot Waking Up...")
    try:
        run_pipeline()
    except Exception as e:
        print(f"❌ Pipeline Error: {e}")
        send_telegram_message(CHAT_ID, f"⚠️ <b>Oracle Error:</b> {e}")
    print("🏁 Run complete. Shutting down until next schedule.")