# strategy_over.py

def analyze_over_1_5(player_a, player_b):
    """
    Analyzes if a match is suitable for Over 1.5 Goals.
    Logic: Looks for combined offensive power.
    """
    
    # Calculate Total Match Goals (TMG) for each player
    # TMG = Average Goals Scored + Average Goals Conceded
    pa_tmg = float(player_a['goals_for_per_match']) + float(player_a['goals_against_per_match'])
    pb_tmg = float(player_b['goals_for_per_match']) + float(player_b['goals_against_per_match'])
    
    # Combined Expectation
    combined_avg_goals = (pa_tmg + pb_tmg) / 2
    
    # STRICT THRESHOLD FOR OVER 1.5
    # We require an expected match total of 3.25 or higher.
    # This provides a safety cushion of roughly 1.75 goals above the 1.5 line.
    if combined_avg_goals >= 3.25:
        return {
            "match": f"{player_a['nickname']} vs {player_b['nickname']}",
            "strategy": "OVER 1.5",
            "score": combined_avg_goals,
            "status": "✅ BET OVER",
            "reason": "High Volatility"
        }
    else:
        return None