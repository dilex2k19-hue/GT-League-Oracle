import requests
import json
import os

def scrape_gt_league_day(start_date, end_date):
    base_url = "https://api.gtleagues.com/api/fixtures"
    limit = 50
    offset = 0
    all_matches = []
    
    print(f"🚀 Starting scrape for period: {start_date} to {end_date}")
    
    while True:
        params = {
            "kickoff": f"between:{start_date},{end_date}",
            "limit": limit,
            "offset": offset,
            "sort": "-kickoff,-matchNr",
            "status": "in:3,5,4,6", 
            "xtc": "true"
        }
        
        # ELITE BROWSER HEADERS - Mimicking a real Chrome browser on the exact domain
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://www.gtleagues.com",
            "Referer": "https://www.gtleagues.com/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            
            # If we get blocked, let's print the exact response text to see if Cloudflare is stopping us
            if response.status_code != 200:
                print(f"❌ Blocked! Status Code: {response.status_code}")
                print(f"Server says: {response.text[:200]}...")
                break
                
            data = response.json()
            
            if not data:
                print("No more matches found on this page. Pagination complete.")
                break
                
            all_matches.extend(data)
            print(f"✅ Fetched {len(data)} matches (Offset: {offset}). Total so far: {len(all_matches)}")
            
            if len(data) < limit:
                break
                
            offset += limit
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error during request: {e}")
            break 
            
    return all_matches

if __name__ == "__main__":
    start = "2026-05-18T22:00:00.000Z"
    end = "2026-05-19T21:59:59.999Z"
    
    matches = scrape_gt_league_day(start, end)
    
    if matches:
        os.makedirs("data", exist_ok=True)
        filename = "data/raw_matches_first_batch.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=4)
            
        print(f"🎉 Success! Saved {len(matches)} matches to {filename}")
    else:
        print("⚠️ No matches were collected.")