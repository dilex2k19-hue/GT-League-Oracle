import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_and_save():
    print("🚀 Launching Spy Bot...")
    
    # 1. Setup Invisible Browser
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 2. Go to the Website
    url = "https://www.gtleagues.com/global-ranking" # Verify this is the exact link for the table
    print(f"🌍 Navigating to {url}...")
    driver.get(url)
    time.sleep(5) # Give it time to load the table

    # 3. Extract Data
    players_data = {}
    
    try:
        # Find all rows in the table
        rows = driver.find_elements(By.TAG_NAME, "tr")
        print(f"👀 Found {len(rows)} rows. Extracting data...")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            
            # We need rows with data, not empty headers
            if len(cols) > 5: 
                try:
                    # IMPORTANT: These indices [1], [2], [8] depend on the website column order.
                    # We may need to adjust them after your first test.
                    name = cols[1].text.strip()
                    gp = int(cols[2].text.replace(',', ''))   # Games Played
                    gf = int(cols[8].text.replace(',', ''))   # Goals For
                    ga = int(cols[9].text.replace(',', ''))   # Goals Against

                    # Save to our dictionary
                    players_data[name] = {
                        "gp": gp,
                        "gf": gf,
                        "ga": ga
                    }
                    print(f"   ✅ Captured: {name}")
                except (ValueError, IndexError):
                    continue # Skip rows that don't have numbers (like headers)

        # 4. Save to JSON File
        if players_data:
            with open("fetched_players.json", "w") as f:
                json.dump(players_data, f, indent=4)
            print(f"\n🎉 Success! Saved {len(players_data)} players to 'fetched_players.json'")
        else:
            print("⚠️ Warning: No players found. Check the column numbers.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_and_save()