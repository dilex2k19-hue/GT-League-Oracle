# ==========================================
# GT LEAGUE: FEATURE CALCULATORS (MATH LAB)
# ==========================================

from datetime import timedelta


# ==========================================
# 1ST CRITERIA CATEGORY: Last 10 Rolling Form
# (Win Rate, Draw Rate, Loss Rate, Avg Goals, 
#  Avg Conceded, Over 2.5 Rate, and Matches Seen)
# ==========================================
def calc_rolling_stats(history_list, limit=10):
    """Calculates basic rates and averages for a given list of past matches."""
    
    # 1. If no history, return the exact criteria labeled with zeros
    if len(history_list) == 0:
        return {
            "win_rate_l10": 0.0,
            "draw_rate_l10": 0.0,
            "loss_rate_l10": 0.0,
            "avg_goals_l10": 0.0,
            "avg_conceded_l10": 0.0,
            "over25_rate_l10": 0.0,
            "matches_seen_l10": 0
        }

    # 2. Grab only the most recent matches up to our limit
    recent_matches = history_list[-limit:]
    matches_seen = len(recent_matches)

    # 3. Count the raw stats
    wins = sum(1 for m in recent_matches if m["result"] == "W")
    draws = sum(1 for m in recent_matches if m["result"] == "D")
    losses = sum(1 for m in recent_matches if m["result"] == "L")
    scored = sum(m["scored"] for m in recent_matches)
    conceded = sum(m["conceded"] for m in recent_matches)
    overs = sum(m["over25"] for m in recent_matches)

    # 4. Return the explicitly named criteria dictionary
    return {
        "win_rate_l10": wins / matches_seen,
        "draw_rate_l10": draws / matches_seen,
        "loss_rate_l10": losses / matches_seen,
        "avg_goals_l10": scored / matches_seen,
        "avg_conceded_l10": conceded / matches_seen,
        "over25_rate_l10": overs / matches_seen,
        "matches_seen_l10": matches_seen
    }
# ==========================================
# END OF 1ST CRITERIA CATEGORY
# ==========================================



# ==========================================
# 2ND CRITERIA CATEGORY: Current Momentum
# (Win Streaks and Over 2.5 Streaks)
# ==========================================
def calc_streaks(history_list):
    """Calculates current consecutive streaks leading up to this match."""
    win_streak = 0
    over_streak = 0
    
    if len(history_list) == 0:
        return {
            "win_streak_current": 0,
            "over_streak_current": 0
        }
        
    # 1. Calculate Win Streak (Read history backwards: newest to oldest)
    for match in reversed(history_list):
        if match["result"] == "W":
            win_streak += 1
        else:
            break
            
    # 2. Calculate Over 2.5 Streak
    for match in reversed(history_list):
        if match["over25"] == 1:
            over_streak += 1
        else:
            break
            
    # 3. Return the explicitly named criteria dictionary
    return {
        "win_streak_current": win_streak,
        "over_streak_current": over_streak
    }
# ==========================================
# END OF 2ND CRITERIA CATEGORY
# ==========================================

# ==========================================
# 3RD CRITERIA CATEGORY: All-Time Head-to-Head (H2H) Context
# (Matches Played, Home Wins, Away Wins, Draws, 
#  Avg Goals, Over 2.5 Rate)
# ==========================================
def calc_h2h_stats(h2h_history_list, current_home_player, current_away_player):
    """Calculates all-time historical stats between two specific players."""
    
    # 1. If they have never played each other, return zeros
    if len(h2h_history_list) == 0:
        return {
            "h2h_matches_played": 0,
            "h2h_home_wins": 0,
            "h2h_away_wins": 0,
            "h2h_draws": 0,
            "h2h_avg_goals": 0.0,
            "h2h_over25_rate": 0.0
        }

    # 2. Get sample size
    matches_played = len(h2h_history_list)
    
    # 3. Count the exact results based on player names
    home_wins = sum(1 for m in h2h_history_list if m["winner"] == current_home_player)
    away_wins = sum(1 for m in h2h_history_list if m["winner"] == current_away_player)
    draws = sum(1 for m in h2h_history_list if m["winner"] == "Draw")
    
    total_goals = sum(m["total_goals"] for m in h2h_history_list)
    overs = sum(m["over25"] for m in h2h_history_list)
    
    # 4. Return the explicitly named criteria dictionary
    return {
        "h2h_matches_played": matches_played,
        "h2h_home_wins": home_wins,
        "h2h_away_wins": away_wins,
        "h2h_draws": draws,
        "h2h_avg_goals": total_goals / matches_played,
        "h2h_over25_rate": overs / matches_played
    }
# ==========================================
# END OF 3RD CRITERIA CATEGORY
# ==========================================

# ==========================================
# 4TH CRITERIA CATEGORY: Volume & Fatigue
# (Matches Played Today, Last 24 Hours, Last 7 Days)
# ==========================================
def calc_volume(history_list, current_timestamp):
    """Calculates how many matches a player has played recently to measure fatigue or warm-up."""
    
    # 1. If they have no history, they are completely fresh!
    if len(history_list) == 0:
        return {
            "daily_matches_played": 0,
            "matches_last_24h": 0,
            "matches_last_7d": 0
        }

    daily_count = 0
    last_24h_count = 0
    last_7d_count = 0

    # 2. Define our exact time boundaries
    one_day_ago = current_timestamp - timedelta(hours=24)
    seven_days_ago = current_timestamp - timedelta(days=7)
    current_date = current_timestamp.date()

    # 3. Read history backwards (newest to oldest)
    for match in reversed(history_list):
        match_time = match["timestamp"]

        # If we reach a match older than 7 days, we can stop searching entirely!
        if match_time < seven_days_ago:
            break
            
        # Count 7-day window
        last_7d_count += 1

        # Count 24-hour window
        if match_time >= one_day_ago:
            last_24h_count += 1

        # Count exact calendar day (midnight to midnight)
        if match_time.date() == current_date:
            daily_count += 1

    # 4. Return the explicitly named criteria dictionary
    return {
        "daily_matches_played": daily_count,
        "matches_last_24h": last_24h_count,
        "matches_last_7d": last_7d_count
    }
# ==========================================
# END OF 4TH CRITERIA CATEGORY
# ==========================================

# ==========================================
# 5TH CRITERIA CATEGORY: Recent Head-to-Head (Last 5 Meetings)
# (L5 Played, L5 Home Wins, L5 Away Wins, L5 Draws,
#  L5 Avg Goals, L5 Over 2.5 Rate)
# ==========================================
def calc_recent_h2h_stats(h2h_history_list, current_home_player, current_away_player):
    """Calculates historical stats between two players, strictly for their last 5 meetings."""

    # 1. If no history, return zeros
    if len(h2h_history_list) == 0:
        return {
            "h2h_l5_played": 0,
            "h2h_l5_home_wins": 0,
            "h2h_l5_away_wins": 0,
            "h2h_l5_draws": 0,
            "h2h_l5_avg_goals": 0.0,
            "h2h_l5_over25_rate": 0.0
        }

    # 2. Grab only the last 5 direct meetings
    recent_h2h = h2h_history_list[-5:]
    matches_played = len(recent_h2h)

    # 3. Count exact results
    home_wins = sum(1 for m in recent_h2h if m["winner"] == current_home_player)
    away_wins = sum(1 for m in recent_h2h if m["winner"] == current_away_player)
    draws = sum(1 for m in recent_h2h if m["winner"] == "Draw")
    
    total_goals = sum(m["total_goals"] for m in recent_h2h)
    overs = sum(m["over25"] for m in recent_h2h)

    # 4. Return explicitly named criteria dictionary
    return {
        "h2h_l5_played": matches_played,
        "h2h_l5_home_wins": home_wins,
        "h2h_l5_away_wins": away_wins,
        "h2h_l5_draws": draws,
        "h2h_l5_avg_goals": total_goals / matches_played,
        "h2h_l5_over25_rate": overs / matches_played
    }
# ==========================================
# END OF 5TH CRITERIA CATEGORY
# ==========================================



# ==========================================
# 6TH CRITERIA CATEGORY: Scoring Consistency & Defense
# (Scored in L5 Rate, Clean Sheet Rate L10)
# ==========================================
def calc_consistency_stats(history_list):
    """Calculates how reliably a player scores goals and keeps clean sheets."""
    
    if len(history_list) == 0:
        return {
            "scored_in_l5_rate": 0.0,
            "clean_sheet_rate_l10": 0.0
        }

    # 1. Scoring Consistency (Last 5)
    l5_history = history_list[-5:]
    l5_seen = len(l5_history)
    games_scored = sum(1 for m in l5_history if m["scored"] > 0)
    scored_in_l5 = games_scored / l5_seen if l5_seen > 0 else 0.0

    # 2. Clean Sheet Rate (Last 10)
    l10_history = history_list[-10:]
    l10_seen = len(l10_history)
    clean_sheets = sum(1 for m in l10_history if m["conceded"] == 0)
    clean_sheet_l10 = clean_sheets / l10_seen if l10_seen > 0 else 0.0

    return {
        "scored_in_l5_rate": scored_in_l5,
        "clean_sheet_rate_l10": clean_sheet_l10
    }
# ==========================================
# END OF 6TH CRITERIA CATEGORY
# ==========================================