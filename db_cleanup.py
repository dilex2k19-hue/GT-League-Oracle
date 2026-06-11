import psycopg2
import psycopg2.extras
import requests
import time
from datetime import datetime, timezone, timedelta

# --- ELITE BROWSER HEADERS ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Origin": "https://www.gtleagues.com",
    "Referer": "https://www.gtleagues.com/"
}

# --- DB CONNECTION ---
DB_URL = "postgresql://postgres.wzziydbnbjpfoxxwevog:behumble250%40@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"

def run_deep_clean():
    print("🧹 Starting Deep Database Cleanup...")
    
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # 1. Find ALL pending matches that have already kicked off
    now_utc = datetime.now(timezone.utc)
    cursor.execute("SELECT * FROM predictions WHERE status = 'Pending' AND kickoff_utc < %s ORDER BY kickoff_utc ASC;", (now_utc,))
    pending_matches = cursor.fetchall()
    
    if not pending_matches:
        print("✅ No stuck pending matches found. Database is clean!")
        cursor.close()
        conn.close()
        return

    print(f"🔍 Found {len(pending_matches)} stuck matches. Fetching historical data...")

    # 2. Find the oldest pending match to know how far back to scrape
    oldest_time = pending_matches[0]['kickoff_utc']
    start_str = (oldest_time - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_str = now_utc.strftime("%Y-%m-%dT%H:%M:%S.999Z")
    
    # 3. Pull all finished matches from GT Leagues API in that window
    url = "https://api.gtleagues.com/api/sports/6/fixtures"
    params = {
        "kickoff": f"between:{start_str},{end_str}",
        "limit": 1000,
        "status": "in:3" # 3 = Finished
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"❌ Failed to reach API. Status code: {response.status_code}")
        return
        
    api_matches = response.json()
    print(f"📦 Downloaded {len(api_matches)} finished matches from API. Grading now...")
    
    fixed_count = 0
    
    # 4. Grade the stuck matches silently
    for p in pending_matches:
        db_time = p['kickoff_utc'].replace(tzinfo=None)
        
        for m in api_matches:
            try:
                h_player = m['participants'][0]['participant']['player']['nickname']
                a_player = m['participants'][1]['participant']['player']['nickname']
                m_time = datetime.strptime(m['kickoff'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=None)
            except Exception:
                continue
                
            # Use our 15-minute tolerance window logic
            time_difference = abs((db_time - m_time).total_seconds())
            
            if p['home_player'] == h_player and p['away_player'] == a_player and time_difference <= 900:
                h_score = m['result']['stats']['home_score']
                a_score = m['result']['stats']['away_score']
                total_goals = h_score + a_score
                
                # Grade it
                won = False
                if p['prediction'] == 'Home Win' and h_score > a_score: won = True
                elif p['prediction'] == 'Away Win' and a_score > h_score: won = True
                elif p['prediction'] == 'Over 2.5' and total_goals > 2: won = True
                
                new_status = "Won" if won else "Lost"
                
                # Commit to DB immediately
                cursor.execute("UPDATE predictions SET status = %s WHERE id = %s", (new_status, p['id']))
                conn.commit()
                
                print(f"🩹 Fixed: {p['home_player']} vs {p['away_player']} -> Marked as {new_status} (Score: {h_score}-{a_score})")
                fixed_count += 1
                break # Move to the next pending match

    cursor.close()
    conn.close()
    print(f"\n🎉 Deep Clean Complete! Fixed {fixed_count} stuck predictions.")

if __name__ == "__main__":
    run_deep_clean()