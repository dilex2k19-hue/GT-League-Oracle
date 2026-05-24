import requests
import psycopg2
import time
from datetime import datetime, timedelta

# Database connection credentials
DB_PARAMS = {
    "dbname": "gt_league_db",
    "user": "gt_admin",
    "password": "password123",
    "host": "localhost",
    "port": "5432"
}

# Elite Browser Headers (From our Phase 3 victory)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.gtleagues.com",
    "Referer": "https://www.gtleagues.com/",
    "Connection": "keep-alive"
}

def get_current_db_count():
    """Checks how many matches we already have in the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM matches;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

def insert_matches(raw_data):
    """Inserts a batch of matches into PostgreSQL."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    inserted = 0
    
    for match in raw_data:
        try:
            match_id = match['id']
            timestamp = match['kickoff']
            
            home_p = next(p for p in match['participants'] if p['side'] == 'home')
            away_p = next(p for p in match['participants'] if p['side'] == 'away')
            
            home_player = home_p['participant']['player']['nickname']
            away_player = away_p['participant']['player']['nickname']
            
            home_goals = match['result']['stats']['home_score']
            away_goals = match['result']['stats']['away_score']
            
            if home_goals is None or away_goals is None:
                continue
            
            over25 = (home_goals + away_goals) > 2
            if home_goals > away_goals:
                winner = 'Home'
            elif away_goals > home_goals:
                winner = 'Away'
            else:
                winner = 'Draw'
                
            cur.execute("""
                INSERT INTO matches (match_id, home_player, away_player, home_goals, away_goals, over25, winner, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (match_id) DO NOTHING;
            """, (match_id, home_player, away_player, home_goals, away_goals, over25, winner, timestamp))
            
            if cur.rowcount > 0:
                inserted += 1
                
        except (KeyError, StopIteration):
            continue
            
    conn.commit()
    cur.close()
    conn.close()
    return inserted

def harvest_history(target_matches=20000):
    """Loops backwards day by day to collect match history."""
    base_url = "https://api.gtleagues.com/api/fixtures"
    
    total_in_db = get_current_db_count()
    print(f"📊 Starting with {total_in_db} matches in database. Target: {target_matches}")
    
    # We start from yesterday (since we already pulled May 18-19 in our test)
    current_end_time = datetime.utcnow().replace(hour=21, minute=59, second=59, microsecond=999000) - timedelta(days=1)
    
    while total_in_db < target_matches:
        current_start_time = current_end_time - timedelta(hours=23, minutes=59, seconds=59)
        
        start_str = current_start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end_str = current_end_time.strftime("%Y-%m-%dT%H:%M:%S.999Z")
        
        print(f"\n🚀 Scraping Day: {start_str[:10]}...")
        
        limit = 100
        offset = 0
        day_matches = []
        
        while True:
            params = {
                "kickoff": f"between:{start_str},{end_str}",
                "limit": limit,
                "offset": offset,
                "sort": "-kickoff,-matchNr",
                "status": "in:3,5,4,6", 
                "xtc": "true"
            }
            
            try:
                response = requests.get(base_url, params=params, headers=HEADERS, timeout=15)
                if response.status_code != 200:
                    print(f"❌ Blocked! Status: {response.status_code}. Sleeping for 30s...")
                    time.sleep(30)
                    continue
                    
                data = response.json()
                if not data:
                    break
                    
                day_matches.extend(data)
                
                if len(data) < limit:
                    break
                    
                offset += limit
                time.sleep(2) # 🛑 CRITICAL: Anti-ban delay between pages
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error: {e}")
                time.sleep(5)
                
        # Insert day's matches into DB
        if day_matches:
            inserted = insert_matches(day_matches)
            total_in_db = get_current_db_count()
            print(f"✅ Inserted {inserted} new matches. Total in DB: {total_in_db}/{target_matches}")
        
        # Move back one more day
        current_end_time -= timedelta(days=1)
        time.sleep(3) # 🛑 CRITICAL: Anti-ban delay between days

    print(f"\n🎉 HARVEST COMPLETE! Reached {total_in_db} matches in database.")

if __name__ == "__main__":
    harvest_history()