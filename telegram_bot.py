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
    """Sends a formatted message safely, chunking by match blocks so HTML tags never break."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Split the massive text by the double line breaks so every match stays whole
    match_blocks = message.split('\n\n')
    
    current_chunk = ""
    
    for block in match_blocks:
        # If adding this next match pushes us over 3500 characters, send what we have first
        if len(current_chunk) + len(block) > 3500:
            payload = {
                "chat_id": target_chat_id,
                "text": current_chunk,
                "parse_mode": "HTML"
            }
            try:
                response = requests.post(url, json=payload)
                if response.status_code != 200:
                    print(f"❌ Telegram API Error: {response.text}")
            except Exception as e:
                print(f"❌ Failed to send Telegram message: {e}")
            
            # Reset the chunk and start with the current block
            current_chunk = block + "\n\n"
            time.sleep(1)  # Polite pause so Telegram doesn't block us for spamming
        else:
            current_chunk += block + "\n\n"
            
    # Send whatever is left in the final chunk
    if current_chunk.strip():
        payload = {
            "chat_id": target_chat_id,
            "text": current_chunk,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"❌ Telegram API Error: {response.text}")
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")

# ---------------------------------------------------------
# 3. THE FEEDBACK LOOP (MANUAL OVERRIDE & SCORE INJECTION)
# ---------------------------------------------------------
def grade_past_predictions():
    """TEMPORARY MANUAL RUN: Grades matches immediately and saves exact scores."""
    now_cat = datetime.now(timezone.utc).astimezone(CAT_TZ)
    
    # --- ⚠️ MANUAL OVERRIDE: THE TIME GATE IS DISABLED ⚠️ ---
    # We commented out the return so the bot runs INSTANTLY for your dashboard test.
    # if not (now_cat.hour == 0 and 30 <= now_cat.minute < 50):
    #     return

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # --- CAPTURE EVERYTHING PENDING ---
    # Look at all pending matches up until RIGHT NOW
    now_utc = datetime.now(timezone.utc)
    cursor.execute(
        "SELECT * FROM predictions WHERE status = 'Pending' AND kickoff_utc <= %s ORDER BY kickoff_utc ASC;",
        (now_utc,)
    )
    pending = cursor.fetchall()
    
    if not pending:
        print("⚠️ No pending matches found to grade right now.")
        cursor.close()
        conn.close()
        return

    print(f"🔄 MANUAL OVERRIDE INITIATED: Grading {len(pending)} pending matches...")
    
    oldest_pending_utc = pending[0]['kickoff_utc']
    api_start_utc = oldest_pending_utc - timedelta(hours=2)
    api_end_utc = datetime.now(timezone.utc)
    
    time_str = f"between:{api_start_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')},{api_end_utc.strftime('%Y-%m-%dT%H:%M:%S.999Z')}"
    
    url = "https://api.gtleagues.com/api/sports/6/fixtures"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Origin": "https://www.gtleagues.com",
        "Referer": "https://www.gtleagues.com/"
    }
    
    finished_matches = []
    offset = 0
    limit = 100
    
    print("📚 Downloading dynamic match history pages...")
    while True:
        params = {"kickoff": time_str, "limit": limit, "offset": offset, "status": "in:3"}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            break
            
        data = response.json()
        if not data:
            break
            
        finished_matches.extend(data)
        offset += limit
        time.sleep(0.5)
        
    goals_results_list = []
    winners_results_list = []
    
    for p in pending:
        for m in finished_matches:
            h_player = m['participants'][0]['participant']['player']['nickname']
            a_player = m['participants'][1]['participant']['player']['nickname']
            
            try:
                m_time = datetime.strptime(m['kickoff'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=None)
                db_time = p['kickoff_utc'].replace(tzinfo=None)
            except Exception:
                continue
            
            time_difference = abs((db_time - m_time).total_seconds())
            max_drift_seconds = 120 * 60 
            
            if p['home_player'] == h_player and p['away_player'] == a_player and time_difference <= max_drift_seconds:
                h_score = m['result']['stats']['home_score']
                a_score = m['result']['stats']['away_score']
                total_goals = h_score + a_score
                
                won = False
                if p['prediction'] == 'Home Win' and h_score > a_score: won = True
                elif p['prediction'] == 'Away Win' and a_score > h_score: won = True
                elif p['prediction'] == 'Over 2.5' and total_goals > 2: won = True
                
                new_status = "Won" if won else "Lost"
                icon = "✅" if won else "❌"
                
                # --- NEW: INJECTING EXACT SCORES INTO THE DATABASE ---
                cursor.execute("""
                    UPDATE predictions 
                    SET status = %s, home_score = %s, away_score = %s 
                    WHERE id = %s
                """, (new_status, h_score, a_score, p['id']))
                conn.commit()
                
                db_utc = p['kickoff_utc']
                if db_utc.tzinfo is None:
                    db_utc = db_utc.replace(tzinfo=timezone.utc)
                kickoff_cat = db_utc.astimezone(CAT_TZ).strftime("%H:%M")
                
                result_text = f"{icon} <b>{p['prediction']}</b> ({p['home_player']} vs {p['away_player']})\n"
                result_text += f"⏰ Time: {kickoff_cat} | Score: {h_score} - {a_score}\n\n"
                
                if p['prediction'] == 'Over 2.5':
                    if not any(item['text'] == result_text for item in goals_results_list):
                        goals_results_list.append({"time_obj": db_utc, "text": result_text})
                else:
                    if not any(item['text'] == result_text for item in winners_results_list):
                        winners_results_list.append({"time_obj": db_utc, "text": result_text})
                    
                break

    cursor.close()
    conn.close()
    
    # Broadcast to Telegram
    report_date = now_cat.strftime('%b %d, %Y (Manual Run)')
    
    if goals_results_list:
        goals_results_list.sort(key=lambda x: x["time_obj"])
        goals_message = f"📊 <b>MANUAL DATABASE UPDATE: OVER 2.5</b> 📊\n\n"
        for item in goals_results_list:
            goals_message += item["text"]
        send_telegram_message(CHAT_ID, goals_message)

    if winners_results_list:
        winners_results_list.sort(key=lambda x: x["time_obj"])
        winners_message = f"📊 <b>MANUAL DATABASE UPDATE: WINNERS</b> 📊\n\n"
        for item in winners_results_list:
            winners_message += item["text"]
        send_telegram_message(WINNERS_CHAT_ID, winners_message)

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
    # Pull the exact kickoff time into memory so we don't block rematches later in the day
    cursor.execute("SELECT home_player, away_player, prediction, kickoff_utc FROM predictions WHERE status = 'Pending';")
    pending_setups = {(row['home_player'], row['away_player'], row['prediction'], row['kickoff_utc']) for row in cursor.fetchall()}
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
    target_window = now_utc + timedelta(minutes=45) 
    
    # Separate lists for true independent market evaluation
    goals_candidates = []
    winners_candidates = []
    
    for match in data:
        if match.get('status') == 0:
            kickoff_utc = datetime.strptime(match['kickoff'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            
            if now_utc <= kickoff_utc <= target_window:
                home_player = match['participants'][0]['participant']['player']['nickname']
                away_player = match['participants'][1]['participant']['player']['nickname']
                
                probs = get_predictions(home_player, away_player)
                if probs:
                    kickoff_cat = kickoff_utc.astimezone(CAT_TZ).strftime("%H:%M CAT")
                    
                    # 1. Add to Goals Market Evaluation
                    goals_candidates.append({
                        "home": home_player, "away": away_player,
                        "kickoff_utc": kickoff_utc, "kickoff_cat": kickoff_cat,
                        "best_pick": "Over 2.5", "confidence": probs["Over 2.5"]
                    })
                    
                    # 2. Add to Winners Market Evaluation (Pick the stronger side)
                    if probs["Home Win"] > probs["Away Win"]:
                        win_pick = "Home Win"
                        win_conf = probs["Home Win"]
                    else:
                        win_pick = "Away Win"
                        win_conf = probs["Away Win"]
                        
                    winners_candidates.append({
                        "home": home_player, "away": away_player,
                        "kickoff_utc": kickoff_utc, "kickoff_cat": kickoff_cat,
                        "best_pick": win_pick, "confidence": win_conf
                    })

    # --- INDEPENDENT SORTING ENGINE ---
    # Sort both lists by highest confidence
    goals_candidates.sort(key=lambda x: x['confidence'], reverse=True)
    winners_candidates.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Extract the Top 2 from each market
    top_goals = goals_candidates[:2]
    top_winners = winners_candidates[:2]
    
    # Combine them for processing
    all_top_picks = top_goals + top_winners

    if not all_top_picks:
        print("⚠️ No matches found in the immediate 45-minute window.")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for match in all_top_picks:
        h_player = match['home']
        a_player = match['away']
        best_pick = match['best_pick']
        conf = match['confidence']
        k_utc = match['kickoff_utc']
        k_cat = match['kickoff_cat']
        
        # Anti-Spam: Skip ONLY if we already sent this exact signal for this EXACT kickoff time
        if (h_player, a_player, best_pick, k_utc) in pending_setups:
            print(f"🔄 Silently skipping {h_player} vs {a_player} (Already pushed earlier for {k_cat})")
            continue
            
        # --- ROUTER LOGIC ---
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