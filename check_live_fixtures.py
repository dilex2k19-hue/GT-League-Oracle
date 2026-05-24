import requests
import json
from datetime import datetime

def check_upcoming():
    url = "https://api.gtleagues.com/api/fixtures"
    
    # Elite browser headers to bypass the HTTP 451 filter
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://www.gtleagues.com",
        "Referer": "https://www.gtleagues.com/"
    }
    
    # 1. Grab the exact current time in UTC
    # 2. Format it to exactly match the API's ISO requirement (e.g., "2026-05-24T16:18:26.000Z")
    current_time_iso = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    params = {
        "limit": 10,
        "kickoff": current_time_iso  # Tell the API to ignore the past
    }
    
    print(f"📡 Pinging GT Leagues for matches starting from: {current_time_iso}...")
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Print the data beautifully so we can read the structure
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed to get data. Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    check_upcoming()