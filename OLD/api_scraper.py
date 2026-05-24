import aiohttp
import asyncio
import json

# 🔴 PASTE THE EXACT URL YOU FOUND IN NETWORK TAB HERE:
API_URL = "https://api.gtleagues.com/api/sports/6/players/standings?limit=1000&offset=0" 
# (I guessed the URL above based on the tagId="soccer" in your JSON. 
# If it fails, replace it with the specific URL you found in DevTools).

async def fetch_players():
    print(f"🚀 Connecting to API: {API_URL}...")

    # We use a "User-Agent" to look like a real Chrome browser so we don't get blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL, headers=headers) as response:
                if response.status == 200:
                    raw_data = await response.json()
                    
                    # 1. Access the list of players inside the "data" key
                    players_list = raw_data.get("data", [])
                    print(f"✅ API Responded! Found {len(players_list)} players.")

                    # 2. Extract only what we need and clean the numbers
                    clean_db = {}
                    
                    for p in players_list:
                        name = p["nickname"]
                        
                        # The API gives strings like "2.24", we need floats 2.24
                        stats = {
                            "gp": int(p["games_played"]),
                            "gf_avg": float(p["goals_for_per_match"]),
                            "ga_avg": float(p["goals_against_per_match"]),
                            # We can also calculate total avg instantly
                            "total_activity": float(p["goals_for_per_match"]) + float(p["goals_against_per_match"])
                        }
                        
                        clean_db[name] = stats

                    # 3. Save to file
                    with open("fetched_players.json", "w") as f:
                        json.dump(clean_db, f, indent=4)
                    
                    print("💾 Database updated: fetched_players.json")
                    
                else:
                    print(f"❌ Error: API returned status code {response.status}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")

# Run the Async function
if __name__ == "__main__":
    asyncio.run(fetch_players())