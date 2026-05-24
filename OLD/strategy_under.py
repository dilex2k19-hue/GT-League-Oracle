# strategy_under.py

def analyze_under_5_5(player_a, player_b):
    """
    Analyzes if a match is suitable for Under 5.5 Goals.
    Logic: Looks for defensive playstyles and low conceding rates.
    """
    
    pa_tmg = float(player_a['goals_for_per_match']) + float(player_a['goals_against_per_match'])
    pb_tmg = float(player_b['goals_for_per_match']) + float(player_b['goals_against_per_match'])
    
    combined_avg_goals = (pa_tmg + pb_tmg) / 2
    
    # STRICT THRESHOLD FOR UNDER 5.5
    # We require an expected match total of 3.8 or LOWER.
    # If the average is 3.8, we have a 1.7 goal cushion before hitting 6 goals.
    if combined_avg_goals <= 3.8:
        return {
            "match": f"{player_a['nickname']} vs {player_b['nickname']}",
            "strategy": "UNDER 5.5",
            "score": combined_avg_goals,
            "status": "🛡️ BET UNDER",
            "reason": "Defensive Lock"
        }
    else:
        return None