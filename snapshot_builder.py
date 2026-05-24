import psycopg2
import psycopg2.extras
from datetime import datetime
import feature_calculators as fc

# ---------------------------------------------------------
# 1. DATABASE CONNECTION
# ---------------------------------------------------------
def get_db_connection():
    """Connects to the PostgreSQL database."""
    return psycopg2.connect(
        dbname="gt_league_db",
        user="postgres",
        password="admin123",
        host="localhost"
    )

# ---------------------------------------------------------
# 2. THE MEMORY TRACKERS
# ---------------------------------------------------------
# This dictionary will hold the ongoing history for every player
# Example: player_history["Siri"] = {"all": [], "home": [], "away": []}
player_history = {}


def initialize_player(player_name):
    """Creates a blank memory file for a new player if they don't exist yet."""
    if player_name not in player_history:
        player_history[player_name] = {
            "all": [],    # Every match played
            "home": [],   # Only matches played on the Home side
            "away": []    # Only matches played on the Away side
        }

# This dictionary will hold the shared history between any two players
h2h_history = {}

def get_h2h_key(player_a, player_b):
    """Creates a consistent shared folder name by sorting their names alphabetically."""
    return tuple(sorted([player_a, player_b]))

# ---------------------------------------------------------
# 3. MAIN ENGINE LOOP
# ---------------------------------------------------------
def build_snapshots():
    print("🚀 Starting the Time Machine...")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Fetch all matches from oldest to newest (CRITICAL FOR NO TIME LEAKAGE)
    print("📥 Fetching historical matches from database...")
    cursor.execute("SELECT * FROM matches ORDER BY timestamp ASC;")
    matches = cursor.fetchall()
    
    print(f"✅ Found {len(matches)} matches. Processing chronologically...")
    
    processed_count = 0
    all_snapshots = []
    
    for match in matches:
        match_id = match['match_id']
        timestamp = match['timestamp']
        home_player = match['home_player']
        away_player = match['away_player']
        
        # 1. Make sure both players exist in our memory tracker
        initialize_player(home_player)
        initialize_player(away_player)
        
        
        # ---------------------------------------------------------
        # 🛑 STOP: THE SNAPSHOT MOMENT
        # ---------------------------------------------------------
        # 1. Get Home Player Features
        home_rolling = fc.calc_rolling_stats(player_history[home_player]["all"])
        home_streaks = fc.calc_streaks(player_history[home_player]["all"])
        home_side = fc.calc_rolling_stats(player_history[home_player]["home"])
        home_consist = fc.calc_consistency_stats(player_history[home_player]["all"])
        home_vol = fc.calc_volume(player_history[home_player]["all"], timestamp)
        
        # 2. Get Away Player Features
        away_rolling = fc.calc_rolling_stats(player_history[away_player]["all"])
        away_streaks = fc.calc_streaks(player_history[away_player]["all"])
        away_side = fc.calc_rolling_stats(player_history[away_player]["away"])
        away_consist = fc.calc_consistency_stats(player_history[away_player]["all"])
        away_vol = fc.calc_volume(player_history[away_player]["all"], timestamp)
        
        # 3. Get Head-to-Head Features
        h2h_key = get_h2h_key(home_player, away_player)
        # Safely get their shared history (if none exists yet, hand it an empty list)
        h2h_hist = h2h_history.get(h2h_key, []) 
        
        h2h_all = fc.calc_h2h_stats(h2h_hist, home_player, away_player)
        h2h_l5 = fc.calc_recent_h2h_stats(h2h_hist, home_player, away_player)

        # 4. Build the Master Snapshot Dictionary
        snapshot = {
            "match_id": match_id,
            "timestamp": timestamp,
            "home_player": home_player,
            "away_player": away_player,
            
            # Target Labels (What the AI will try to predict)
            "target_home_win": 1 if match['winner'] == "Home" else 0,
            "target_away_win": 1 if match['winner'] == "Away" else 0,
            "target_over25": 1 if match['over25'] else 0,
            "match_hour": timestamp.hour,

            # Home Form
            "home_win_rate_l10": home_rolling["win_rate_l10"],
            "home_draw_rate_l10": home_rolling["draw_rate_l10"],
            "home_loss_rate_l10": home_rolling["loss_rate_l10"],
            "home_avg_goals_l10": home_rolling["avg_goals_l10"],
            "home_avg_conceded_l10": home_rolling["avg_conceded_l10"],
            "home_over25_rate_l10": home_rolling["over25_rate_l10"],
            "home_matches_seen_l10": home_rolling["matches_seen_l10"],
            
            # Home Streaks & Consistency
            "home_win_streak_current": home_streaks["win_streak_current"],
            "home_over_streak_current": home_streaks["over_streak_current"],
            "home_scored_in_l5_rate": home_consist["scored_in_l5_rate"],
            "home_clean_sheet_rate_l10": home_consist["clean_sheet_rate_l10"],
            
            # Home Side Only
            "home_win_rate_side_l10": home_side["win_rate_l10"],
            "home_avg_goals_side_l10": home_side["avg_goals_l10"],
            "home_side_matches_seen": home_side["matches_seen_l10"],
            
            # Home Volume
            "home_daily_matches_played": home_vol["daily_matches_played"],
            "home_matches_last_24h": home_vol["matches_last_24h"],
            "home_matches_last_7d": home_vol["matches_last_7d"],

            # Away Form
            "away_win_rate_l10": away_rolling["win_rate_l10"],
            "away_draw_rate_l10": away_rolling["draw_rate_l10"],
            "away_loss_rate_l10": away_rolling["loss_rate_l10"],
            "away_avg_goals_l10": away_rolling["avg_goals_l10"],
            "away_avg_conceded_l10": away_rolling["avg_conceded_l10"],
            "away_over25_rate_l10": away_rolling["over25_rate_l10"],
            "away_matches_seen_l10": away_rolling["matches_seen_l10"],
            
            # Away Streaks & Consistency
            "away_win_streak_current": away_streaks["win_streak_current"],
            "away_over_streak_current": away_streaks["over_streak_current"],
            "away_scored_in_l5_rate": away_consist["scored_in_l5_rate"],
            "away_clean_sheet_rate_l10": away_consist["clean_sheet_rate_l10"],
            
            # Away Side Only
            "away_win_rate_side_l10": away_side["win_rate_l10"],
            "away_avg_goals_side_l10": away_side["avg_goals_l10"],
            "away_side_matches_seen": away_side["matches_seen_l10"],
            
            # Away Volume
            "away_daily_matches_played": away_vol["daily_matches_played"],
            "away_matches_last_24h": away_vol["matches_last_24h"],
            "away_matches_last_7d": away_vol["matches_last_7d"],

            # H2H All Time
            "h2h_matches_played": h2h_all["h2h_matches_played"],
            "h2h_home_wins": h2h_all["h2h_home_wins"],
            "h2h_away_wins": h2h_all["h2h_away_wins"],
            "h2h_draws": h2h_all["h2h_draws"],
            "h2h_avg_goals": h2h_all["h2h_avg_goals"],
            "h2h_over25_rate": h2h_all["h2h_over25_rate"],

            # H2H Last 5
            "h2h_l5_played": h2h_l5["h2h_l5_played"],
            "h2h_l5_home_wins": h2h_l5["h2h_l5_home_wins"],
            "h2h_l5_away_wins": h2h_l5["h2h_l5_away_wins"],
            "h2h_l5_draws": h2h_l5["h2h_l5_draws"],
            "h2h_l5_avg_goals": h2h_l5["h2h_l5_avg_goals"],
            "h2h_l5_over25_rate": h2h_l5["h2h_l5_over25_rate"],

            # Margins & Differentials
            "win_rate_diff": round(home_rolling["win_rate_l10"] - away_rolling["win_rate_l10"], 4),
            "avg_goals_diff": round(home_rolling["avg_goals_l10"] - away_rolling["avg_goals_l10"], 4),
            "over25_rate_diff": round(home_rolling["over25_rate_l10"] - away_rolling["over25_rate_l10"], 4),

            # Placeholders for future advanced features
            "home_weighted_winrate": 0.0,
            "away_weighted_winrate": 0.0
        }
        
        # 5. Save this match to our master list
        all_snapshots.append(snapshot)
            
        # ---------------------------------------------------------
        # 🟢 GO: UPDATE THE MEMORY
        # ---------------------------------------------------------
        # Now that the snapshot is taken, we update the player's history
        # so it is ready for their NEXT match.
        
        # Create the basic match result dictionary
        home_result = {
            "result": "W" if match['winner'] == "Home" else "D" if match['winner'] == "Draw" else "L",
            "scored": match['home_goals'],
            "conceded": match['away_goals'],
            "over25": match['over25'],
            "timestamp": timestamp
        }
        
        away_result = {
            "result": "W" if match['winner'] == "Away" else "D" if match['winner'] == "Draw" else "L",
            "scored": match['away_goals'],
            "conceded": match['home_goals'],
            "over25": match['over25'],
            "timestamp": timestamp
        }
        
        # ---------------------------------------------------------
        # UPDATE SHARED H2H MEMORY
        # ---------------------------------------------------------
        h2h_key = get_h2h_key(home_player, away_player)
        
        # If they've never played before, create their shared folder
        if h2h_key not in h2h_history:
            h2h_history[h2h_key] = []
            
        # Create a simple H2H result record
        h2h_result = {
            "winner": match['winner'],
            "total_goals": match['home_goals'] + match['away_goals'],
            "over25": match['over25']
        }
        
        # Add it to their shared history
        h2h_history[h2h_key].append(h2h_result)


        # Add to the "all" history
        player_history[home_player]["all"].append(home_result)
        player_history[away_player]["all"].append(away_result)
        
        # Add to the side-specific history
        player_history[home_player]["home"].append(home_result)
        player_history[away_player]["away"].append(away_result)
        
        processed_count += 1
        
        # Print progress every 5000 matches
        if processed_count % 5000 == 0:
            print(f"⏳ Processed {processed_count} matches...")

    print(f"🎉 Time Machine loop complete! Built {len(all_snapshots)} snapshots.")
    print("💾 Saving snapshots to PostgreSQL (this might take a few seconds)...")

    # 1. Get the column names from our first snapshot dictionary
    columns = list(all_snapshots[0].keys())
    
    # 2. Build the SQL query string
    # ON CONFLICT DO NOTHING ensures if we run this script twice, it won't crash from duplicate matches
    query = "INSERT INTO match_features ({}) VALUES %s ON CONFLICT (match_id) DO NOTHING".format(
        ', '.join(columns)
    )
    
    # 3. Extract just the raw numbers/values from every snapshot
    values = [[snapshot[col] for col in columns] for snapshot in all_snapshots]
    
    # 4. Perform the bulk insert!
    psycopg2.extras.execute_values(cursor, query, values)
    conn.commit()
    
    print("✅ All snapshots successfully saved to the match_features table!")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    build_snapshots()