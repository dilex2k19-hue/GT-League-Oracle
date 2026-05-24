import psycopg2

# Database connection credentials
DB_PARAMS = {
    "dbname": "gt_league_db",
    "user": "gt_admin",
    "password": "password123",
    "host": "localhost",
    "port": "5432"
}

def build_player_features():
    """Aggregates all match data to build statistical profiles for every player."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    print("🔄 Crunching numbers for Player Profiles...")
    
    # We use a CTE (Common Table Expression) to combine home and away performances,
    # then aggregate them into exact win rates and goal averages.
    cur.execute("""
        WITH player_stats AS (
            SELECT home_player AS player,
                   CASE WHEN winner = 'Home' THEN 1.0 ELSE 0.0 END AS win,
                   home_goals AS goals_scored,
                   away_goals AS goals_conceded,
                   CASE WHEN over25 THEN 1.0 ELSE 0.0 END AS is_over25
            FROM matches
            UNION ALL
            SELECT away_player AS player,
                   CASE WHEN winner = 'Away' THEN 1.0 ELSE 0.0 END AS win,
                   away_goals AS goals_scored,
                   home_goals AS goals_conceded,
                   CASE WHEN over25 THEN 1.0 ELSE 0.0 END AS is_over25
            FROM matches
        )
        INSERT INTO players (player_name, win_rate, avg_goals, avg_conceded, over25_rate)
        SELECT player,
               ROUND(AVG(win)::numeric, 4) AS win_rate,
               ROUND(AVG(goals_scored)::numeric, 2) AS avg_goals,
               ROUND(AVG(goals_conceded)::numeric, 2) AS avg_conceded,
               ROUND(AVG(is_over25)::numeric, 4) AS over25_rate
        FROM player_stats
        GROUP BY player
        ON CONFLICT (player_name) 
        DO UPDATE SET 
            win_rate = EXCLUDED.win_rate,
            avg_goals = EXCLUDED.avg_goals,
            avg_conceded = EXCLUDED.avg_conceded,
            over25_rate = EXCLUDED.over25_rate;
    """)
    
    conn.commit()
    print(f"✅ Player features updated successfully. Processed {cur.rowcount} players.")
    cur.close()
    conn.close()

def build_h2h_features():
    """Aggregates all matches to build Head-to-Head histories between specific players."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    print("🔄 Crunching numbers for Head-to-Head match-ups...")
    
    # LEAST and GREATEST ensure 'Eros vs Lio' and 'Lio vs Eros' group into the exact same H2H record.
    cur.execute("""
        WITH h2h_base AS (
            SELECT LEAST(home_player, away_player) AS p_a,
                   GREATEST(home_player, away_player) AS p_b,
                   CASE WHEN LEAST(home_player, away_player) = home_player AND winner = 'Home' THEN 1
                        WHEN LEAST(home_player, away_player) = away_player AND winner = 'Away' THEN 1
                        ELSE 0 END AS p_a_win,
                   (home_goals + away_goals) AS total_goals,
                   CASE WHEN over25 THEN 1.0 ELSE 0.0 END AS is_over25
            FROM matches
        )
        INSERT INTO h2h (player_a, player_b, matches_played, player_a_wins, avg_goals, over25_rate)
        SELECT p_a, 
               p_b,
               COUNT(*) AS matches_played,
               SUM(p_a_win) AS player_a_wins,
               ROUND(AVG(total_goals)::numeric, 2) AS avg_goals,
               ROUND(AVG(is_over25)::numeric, 4) AS over25_rate
        FROM h2h_base
        GROUP BY p_a, p_b
        ON CONFLICT (player_a, player_b) 
        DO UPDATE SET 
            matches_played = EXCLUDED.matches_played,
            player_a_wins = EXCLUDED.player_a_wins,
            avg_goals = EXCLUDED.avg_goals,
            over25_rate = EXCLUDED.over25_rate;
    """)
    
    conn.commit()
    print(f"✅ Head-to-Head features updated successfully. Processed {cur.rowcount} unique matchups.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("🚀 Starting Feature Engine...")
    build_player_features()
    build_h2h_features()
    print("🎉 Feature Engineering Complete!")