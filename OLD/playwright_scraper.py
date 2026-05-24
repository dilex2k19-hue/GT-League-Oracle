import asyncio
import json
from playwright.async_api import async_playwright

# The API URL you found in your network tab
API_URL = "https://api.gtleagues.com/api/sports/6/players/standings?limit=1000&offset=0"

async def scrape_with_auth():
    print("🚀 Launching Playwright (Headless)...")
    
    async with async_playwright() as p:
        # 1. Launch Browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 2. Go to Homepage FIRST to get the "Auth" (Cookies/Headers)
        print("🌍 Visiting homepage to initialize session...")
        try:
            await page.goto("https://www.gtleagues.com", wait_until="networkidle")
            # Wait a moment for any background auth challenges (Cloudflare/etc) to pass
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"⚠️ Homepage load warning: {e}")

        # 3. Now use the TRUSTED context to hit the API
        print(f"⚡ Fetching API data from: {API_URL}")
        response = await context.request.get(API_URL)

        if response.status == 200:
            data = await response.json()
            players_list = data.get("data", [])
            print(f"✅ Success! API Status: 200. Found {len(players_list)} players.")
            
            # 4. Clean and Format Data for validator.py
            clean_db = {}
            for p in players_list:
                name = p["nickname"]
                try:
                    # Convert strings "2.24" to floats 2.24
                    gp = int(p["games_played"])
                    gf_avg = float(p["goals_for_per_match"])
                    ga_avg = float(p["goals_against_per_match"])
                    
                    # Calculate total immediately
                    total_avg = gf_avg + ga_avg
                    
                    clean_db[name] = {
                        "gp": gp,
                        "gf_avg": gf_avg,
                        "ga_avg": ga_avg,
                        "total_activity": round(total_avg, 2)
                    }
                except (ValueError, KeyError):
                    continue

            # 5. Save to File
            with open("fetched_players.json", "w") as f:
                json.dump(clean_db, f, indent=4)
            print("💾 Database updated: fetched_players.json")

        else:
            print(f"❌ API Error: {response.status} - {response.status_text}")
            print("The website might be blocking this specific IP or User Agent.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_with_auth())