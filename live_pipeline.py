import requests
import psycopg2
import psycopg2.extras
import pandas as pd
import joblib
from datetime import datetime, timezone, timedelta
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
import feature_calculators as fc

# ---------------------------------------------------------
# 1. LOAD THE AI BRAINS
# ---------------------------------------------------------
print("🧠 Waking up the AI Specialists...")
scaler = joblib.load('models/scaler.pkl')
home_model = joblib.load('models/rf_home_model.pkl')
away_model = joblib.load('models/rf_away_model.pkl')
over25_model = joblib.load('models/rf_over25_model.pkl')

# ---------------------------------------------------------
# 2. DATABASE FUNCTIONS
# ---------------------------------------------------------
def get_db_connection():
    return psycopg2.connect(dbname="gt_league_db", user="postgres", password="admin123", host="localhost")

def fetch_player_history(player_name, cursor):
    cursor.execute("""
        SELECT * FROM matches 
        WHERE home_player = %s OR away_player = %s 
        ORDER BY timestamp ASC
    """, (player_name, player_name))
    
    matches = cursor.fetchall()
    history = {"all": [], "home": [], "away": []}
    
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
        if is_home: history["home"].append(result)
        else: history["away"].append(result)
            
    return history

def fetch_h2h_history(home_player, away_player, cursor):
    cursor.execute("""
        SELECT * FROM matches 
        WHERE (home_player = %s AND away_player = %s) 
           OR (home_player = %s AND away_player = %s)
        ORDER BY timestamp ASC
    """, (home_player, away_player, away_player, home_player))
    
    matches = cursor.fetchall()
    h2h_hist = []
    for match in matches:
        h2h_hist.append({
            "winner": match['winner'],
            "total_goals": match['home_goals'] + match['away_goals'],
            "over25": match['over25']
        })
    return h2h_hist

# ---------------------------------------------------------
# 3. PREDICTION ENGINE
# ---------------------------------------------------------
def get_predictions(home_player, away_player):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    home_hist = fetch_player_history(home_player, cursor)
    away_hist = fetch_player_history(away_player, cursor)
    h2h_hist = fetch_h2h_history(home_player, away_player, cursor)
    
    cursor.close()
    conn.close()
    
    # If a player is brand new and has no history, we skip them
    if not home_hist["all"] or not away_hist["all"]:
        return None

    now = datetime.now()
    
    # Calculate all 55 features
    home_rolling = fc.calc_rolling_stats(home_hist["all"])
    home_streaks = fc.calc_streaks(home_hist["all"])
    home_side = fc.calc_rolling_stats(home_hist["home"])
    home_consist = fc.calc_consistency_stats(home_hist["all"])
    home_vol = fc.calc_volume(home_hist["all"], now)
    
    away_rolling = fc.calc_rolling_stats(away_hist["all"])
    away_streaks = fc.calc_streaks(away_hist["all"])
    away_side = fc.calc_rolling_stats(away_hist["away"])
    away_consist = fc.calc_consistency_stats(away_hist["all"])
    away_vol = fc.calc_volume(away_hist["all"], now)
    
    h2h_all = fc.calc_h2h_stats(h2h_hist, home_player, away_player)
    h2h_l5 = fc.calc_recent_h2h_stats(h2h_hist, home_player, away_player)

    snapshot = {
        "match_hour": now.hour,
        "home_win_rate_l10": home_rolling["win_rate_l10"],
        "home_draw_rate_l10": home_rolling["draw_rate_l10"],
        "home_loss_rate_l10": home_rolling["loss_rate_l10"],
        "home_avg_goals_l10": home_rolling["avg_goals_l10"],
        "home_avg_conceded_l10": home_rolling["avg_conceded_l10"],
        "home_over25_rate_l10": home_rolling["over25_rate_l10"],
        "home_matches_seen_l10": home_rolling["matches_seen_l10"],
        "home_win_streak_current": home_streaks["win_streak_current"],
        "home_over_streak_current": home_streaks["over_streak_current"],
        "home_scored_in_l5_rate": home_consist["scored_in_l5_rate"],
        "home_clean_sheet_rate_l10": home_consist["clean_sheet_rate_l10"],
        "home_win_rate_side_l10": home_side["win_rate_l10"],
        "home_avg_goals_side_l10": home_side["avg_goals_l10"],
        "home_side_matches_seen": home_side["matches_seen_l10"],
        "home_daily_matches_played": home_vol["daily_matches_played"],
        "home_matches_last_24h": home_vol["matches_last_24h"],
        "home_matches_last_7d": home_vol["matches_last_7d"],
        "away_win_rate_l10": away_rolling["win_rate_l10"],
        "away_draw_rate_l10": away_rolling["draw_rate_l10"],
        "away_loss_rate_l10": away_rolling["loss_rate_l10"],
        "away_avg_goals_l10": away_rolling["avg_goals_l10"],
        "away_avg_conceded_l10": away_rolling["avg_conceded_l10"],
        "away_over25_rate_l10": away_rolling["over25_rate_l10"],
        "away_matches_seen_l10": away_rolling["matches_seen_l10"],
        "away_win_streak_current": away_streaks["win_streak_current"],
        "away_over_streak_current": away_streaks["over_streak_current"],
        "away_scored_in_l5_rate": away_consist["scored_in_l5_rate"],
        "away_clean_sheet_rate_l10": away_consist["clean_sheet_rate_l10"],
        "away_win_rate_side_l10": away_side["win_rate_l10"],
        "away_avg_goals_side_l10": away_side["avg_goals_l10"],
        "away_side_matches_seen": away_side["matches_seen_l10"],
        "away_daily_matches_played": away_vol["daily_matches_played"],
        "away_matches_last_24h": away_vol["matches_last_24h"],
        "away_matches_last_7d": away_vol["matches_last_7d"],
        "h2h_matches_played": h2h_all["h2h_matches_played"],
        "h2h_home_wins": h2h_all["h2h_home_wins"],
        "h2h_away_wins": h2h_all["h2h_away_wins"],
        "h2h_draws": h2h_all["h2h_draws"],
        "h2h_avg_goals": h2h_all["h2h_avg_goals"],
        "h2h_over25_rate": h2h_all["h2h_over25_rate"],
        "h2h_l5_played": h2h_l5["h2h_l5_played"],
        "h2h_l5_home_wins": h2h_l5["h2h_l5_home_wins"],
        "h2h_l5_away_wins": h2h_l5["h2h_l5_away_wins"],
        "h2h_l5_draws": h2h_l5["h2h_l5_draws"],
        "h2h_l5_avg_goals": h2h_l5["h2h_l5_avg_goals"],
        "h2h_l5_over25_rate": h2h_l5["h2h_l5_over25_rate"],
        "win_rate_diff": round(home_rolling["win_rate_l10"] - away_rolling["win_rate_l10"], 4),
        "avg_goals_diff": round(home_rolling["avg_goals_l10"] - away_rolling["avg_goals_l10"], 4),
        "over25_rate_diff": round(home_rolling["over25_rate_l10"] - away_rolling["over25_rate_l10"], 4),
        "home_weighted_winrate": 0.0,
        "away_weighted_winrate": 0.0
    }
    
    df = pd.DataFrame([snapshot])
    
    # --- ALIGNMENT PROTOCOL ---
    # The AI expects the columns in the exact same order it was trained on.
    # scaler.feature_names_in_ contains that exact list!
    expected_features = scaler.feature_names_in_
    
    # 1. Safely add any missing columns as 0.0 just in case
    for col in expected_features:
        if col not in df.columns:
            df[col] = 0.0
            
    # 2. Force our live dataframe to re-order itself to match the AI's memory
    df = df[expected_features]
    # --------------------------
    
    X_scaled = scaler.transform(df)
    
    return {
        "Home Win": round(home_model.predict_proba(X_scaled)[0][1] * 100, 1),
        "Away Win": round(away_model.predict_proba(X_scaled)[0][1] * 100, 1),
        "Over 2.5": round(over25_model.predict_proba(X_scaled)[0][1] * 100, 1)
    }

# ---------------------------------------------------------
# 4. THE LIVE SCANNER & FILTER
# ---------------------------------------------------------
def scan_live_market():
    # Using your exactly discovered sports API endpoint
    url = "https://api.gtleagues.com/api/sports/6/fixtures"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Origin": "https://www.gtleagues.com",
        "Referer": "https://www.gtleagues.com/"
    }
    
    # Let's dynamically build the "between" 24-hour window just like their website does
    now_utc = datetime.now(timezone.utc)
    start_of_day = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1, microseconds=-1)
    
    time_str = f"between:{start_of_day.strftime('%Y-%m-%dT%H:%M:%S.000Z')},{end_of_day.strftime('%Y-%m-%dT%H:%M:%S.999Z')}"
    
    # Your discovered parameters
    params = {
        "kickoff": time_str,
        "limit": 1000,
        "offset": 0,
        "sort": "kickoff,matchNr",
        "status": "in:1,0"  # 1 = Live, 0 = Upcoming
    }
    
    print("📡 Pulling today's master schedule from GT Leagues...")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"❌ Failed to reach API. Status: {response.status_code}")
        return

    data = response.json()
    
    # We want matches starting between NOW and 45 MINUTES from now
    target_window = now_utc + timedelta(minutes=45) 
    
    analyzed_matches = []
    
    for match in data:
        # Strict check: We ONLY want status 0 (Not Started). 
        # If it's 1 (Live), we skip it because it's too late to bet!
        if match.get('status') == 0:
            kickoff_str = match['kickoff']
            kickoff_utc = datetime.strptime(kickoff_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            
            # The Time Filter: Is it in the future, but happening soon?
            if now_utc <= kickoff_utc <= target_window:
                home_player = match['participants'][0]['participant']['player']['nickname']
                away_player = match['participants'][1]['participant']['player']['nickname']
                
                print(f"🔍 Found upcoming match: {home_player} vs {away_player} (Kickoff: {kickoff_utc.strftime('%H:%M')} UTC). Calculating AI read...")
                
                # Fetch AI Predictions
                probs = get_predictions(home_player, away_player)
                if probs:
                    best_pick = max(probs, key=probs.get)
                    confidence = probs[best_pick]
                    
                    analyzed_matches.append({
                        "match": f"{home_player} vs {away_player}",
                        "kickoff": kickoff_utc.strftime("%H:%M UTC"),
                        "best_pick": best_pick,
                        "confidence": confidence,
                        "all_probs": probs
                    })
    
    # ---------------------------------------------------------
    # 5. PUBLISH THE ELITE TOP 2
    # ---------------------------------------------------------
    if not analyzed_matches:
        print("\n⚠️ No upcoming matches found in the next 45 minutes.")
        return
        
    # Sort the matches from highest confidence to lowest
    analyzed_matches.sort(key=lambda x: x['confidence'], reverse=True)
    
    print("\n===============================================")
    print("🏆 TOP 2 ELITE PREDICTIONS (Next 45 Mins) 🏆")
    print("===============================================\n")
    
    for i, match in enumerate(analyzed_matches[:2]): # Slice the top 2
        print(f"🔥 PICK #{i+1}: {match['match']}")
        print(f"⏰ Time: {match['kickoff']}")
        print(f"🎯 Prediction: {match['best_pick']} ({match['confidence']}% Confidence)")
        print(f"📊 Full AI Read: Home {match['all_probs']['Home Win']}% | Away {match['all_probs']['Away Win']}% | Over 2.5: {match['all_probs']['Over 2.5']}%\n")
    print("===============================================\n")

if __name__ == "__main__":
    scan_live_market()