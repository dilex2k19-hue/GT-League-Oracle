import os
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta, timezone

# Elite Browser Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Origin": "https://www.gtleagues.com",
    "Referer": "https://www.gtleagues.com/"
}

def get_db_connection():
    """Connects to Cloud DB if on GitHub, otherwise uses local DB."""
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    else:
        # Local fallback
        return psycopg2.connect(dbname="gt_league_db", user="postgres", password="admin123", host="localhost")

def update_live_database():
    print("🔄 Starting Live Database Update...")
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Find the newest match in our memory
    cur.execute("SELECT MAX(timestamp) FROM matches;")
    latest_timestamp = cur.fetchone()[0]

    if not latest_timestamp:
        print("⚠️ Database is empty. Please run migration script first.")
        return

    print(f"📅 Newest match in memory: {latest_timestamp}")

    # 2. Scrape recent matches (Last 24 hours to catch up)
    now_utc = datetime.now(timezone.utc)
    start_time = now_utc - timedelta(days=1)

    start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_str = now_utc.strftime("%Y-%m-%dT%H:%M:%S.999Z")

    url = "https://api.gtleagues.com/api/sports/6/fixtures"
    params = {
        "kickoff": f"between:{start_str},{end_str}",
        "limit": 1000,
        "status": "in:3" # 3 = Finished matches
    }

    print("📡 Fetching recent finished matches from API...")
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return

    data = response.json()
    new_matches = []

    for match in data:
        try:
            # Parse the API timestamp into a Python datetime object
            match_time = datetime.strptime(match['kickoff'], "%Y-%m-%dT%H:%M:%S.%fZ")

            # Only process matches that are strictly NEWER than our memory
            if match_time > latest_timestamp:
                home_p = match['participants'][0]['participant']['player']['nickname']
                away_p = match['participants'][1]['participant']['player']['nickname']
                home_goals = match['result']['stats']['home_score']
                away_goals = match['result']['stats']['away_score']

                over25 = (home_goals + away_goals) > 2
                winner = 'Home' if home_goals > away_goals else 'Away' if away_goals > home_goals else 'Draw'

                new_matches.append((home_p, away_p, home_goals, away_goals, winner, over25, match_time))
        except Exception as e:
            continue

    # 3. Insert only the new matches
    if new_matches:
        print(f"📦 Found {len(new_matches)} NEW matches! Injecting into memory...")
        insert_query = """
            INSERT INTO matches (home_player, away_player, home_goals, away_goals, winner, over25, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        psycopg2.extras.execute_batch(cur, insert_query, new_matches)
        conn.commit()
        print("✅ Database successfully updated!")
    else:
        print("✅ Database is already up to date. No new matches found.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    update_live_database()