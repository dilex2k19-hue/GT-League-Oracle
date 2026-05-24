import json
import psycopg2
import os

# Database connection credentials
DB_PARAMS = {
    "dbname": "gt_league_db",
    "user": "gt_admin",
    "password": "password123",
    "host": "localhost",
    "port": "5432"
}

def setup_database():
    """Creates the necessary tables if they do not exist."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # 1. Matches Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id VARCHAR(50) PRIMARY KEY,
            home_player VARCHAR(100),
            away_player VARCHAR(100),
            home_goals INTEGER,
            away_goals INTEGER,
            over25 BOOLEAN,
            winner VARCHAR(10),
            timestamp TIMESTAMP
        );
    """)
    
    # 2. Players Table (To be populated later in Phase 6)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_name VARCHAR(100) PRIMARY KEY,
            win_rate FLOAT DEFAULT 0,
            avg_goals FLOAT DEFAULT 0,
            avg_conceded FLOAT DEFAULT 0,
            over25_rate FLOAT DEFAULT 0
        );
    """)

    # 3. H2H Table (To be populated later in Phase 6)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS h2h (
            player_a VARCHAR(100),
            player_b VARCHAR(100),
            matches_played INTEGER DEFAULT 0,
            player_a_wins INTEGER DEFAULT 0,
            avg_goals FLOAT DEFAULT 0,
            over25_rate FLOAT DEFAULT 0,
            PRIMARY KEY (player_a, player_b)
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database tables created successfully.")

def insert_matches_from_json(filepath):
    """Parses raw JSON matches and inserts them into the database."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    inserted_count = 0
    skipped_count = 0
    
    for match in raw_data:
        try:
            match_id = match['id']
            timestamp = match['kickoff']
            
            # Locate home and away participants from the nested JSON
            home_p = next(p for p in match['participants'] if p['side'] == 'home')
            away_p = next(p for p in match['participants'] if p['side'] == 'away')
            
            home_player = home_p['participant']['player']['nickname']
            away_player = away_p['participant']['player']['nickname']
            
            # Extract scores
            home_goals = match['result']['stats']['home_score']
            away_goals = match['result']['stats']['away_score']
            
            # Skip if match was voided/has missing score data
            if home_goals is None or away_goals is None:
                skipped_count += 1
                continue
            
            # Calculate our predictive features
            over25 = (home_goals + away_goals) > 2
            
            if home_goals > away_goals:
                winner = 'Home'
            elif away_goals > home_goals:
                winner = 'Away'
            else:
                winner = 'Draw'
                
            # Insert into database (Ignore if match_id already exists)
            cur.execute("""
                INSERT INTO matches (match_id, home_player, away_player, home_goals, away_goals, over25, winner, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (match_id) DO NOTHING;
            """, (match_id, home_player, away_player, home_goals, away_goals, over25, winner, timestamp))
            
            if cur.rowcount > 0:
                inserted_count += 1
                
        except (KeyError, StopIteration) as e:
            # Catch incomplete JSON objects
            skipped_count += 1
            continue
            
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Successfully inserted {inserted_count} new matches into the database.")
    if skipped_count > 0:
        print(f"⚠️ Skipped {skipped_count} matches due to missing or voided data.")

if __name__ == "__main__":
    print("🛠️ Setting up database schema...")
    setup_database()
    print("📥 Parsing and inserting raw matches...")
    insert_matches_from_json("data/raw_matches_first_batch.json")