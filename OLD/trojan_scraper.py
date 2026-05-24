import asyncio
import json
from playwright.async_api import async_playwright

# The API URL
API_URL = "https://api.gtleagues.com/api/sports/6/players/standings?limit=1000&offset=0"

async def scrape_via_browser_nav():
    print("🚀 Launching Browser (Trojan Mode)...")
    
    async with async_playwright() as p:
        # 1. Launch Browser
        # If this fails, change headless=False to see what is happening on screen
        browser = await p.chromium.launch(headless=True) 
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 2. Go to Homepage FIRST (To look like a human and get cookies)
        print("🌍 Visiting homepage to authenticate...")
        try:
            await page.goto("https://www.gtleagues.com", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000) # Wait 3 seconds
        except Exception as e:
            print(f"⚠️ Homepage warning: {e}")

        # 3. Navigate DIRECTLY to the JSON Link
        print(f"⚡ Navigating to API Link: {API_URL}")
        response = await page.goto(API_URL)

        # 4. Check if it worked
        if response.status == 200:
            print("✅ Access Granted! Reading data from screen...")
            
            # Extract the text from the browser body (which is the JSON)
            json_text = await page.inner_text("body")
            
            try:
                data = json.loads(json_text)
                players_list = data.get("data", [])
                print(f"🎉 Found {len(players_list)} players.")

                # 5. Save and Clean
                clean_db = {}
                for p in players_list:
                    name = p.get("nickname")
                    if not name: continue
                    
                    try:
                        gp = int(p["games_played"])
                        gf_avg = float(p["goals_for_per_match"])
                        ga_avg = float(p["goals_against_per_match"])
                        
                        clean_db[name] = {
                            "gp": gp,
                            "gf_avg": gf_avg,
                            "ga_avg": ga_avg,
                            "total_activity": round(gf_avg + ga_avg, 2)
                        }
                    except:
                        continue

                with open("fetched_players.json", "w") as f:
                    json.dump(clean_db, f, indent=4)
                print("💾 Database saved to fetched_players.json")

            except json.JSONDecodeError:
                print("❌ Error: The page did not return valid JSON. It might be a block page.")
                print("Page content preview:", json_text[:100])
        
        elif response.status == 451:
            print("❌ Still blocked (451). The site is blocking your IP region.")
        else:
            print(f"❌ Failed with status: {response.status}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_via_browser_nav())