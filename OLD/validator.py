import json
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import os

# --- 1. LOAD DATA ---
FILE_NAME = "fetched_players.json"

try:
    if not os.path.exists(FILE_NAME):
        print(f"❌ Error: '{FILE_NAME}' is missing.")
        exit()

    with open(FILE_NAME, "r") as f:
        raw_json = json.load(f)
        
    # Get the list of players
    players_list = raw_json.get('data', [])
    
    if not players_list:
        print("❌ Error: No player data found in file.")
        exit()
        
    # Create Database (Dictionary)
    players_db = {p['nickname'].lower(): p for p in players_list}
    
    # Create Suggestion List for Autocomplete
    suggestion_list = [p['nickname'] for p in players_list]
    player_completer = WordCompleter(suggestion_list, ignore_case=True)
    
    print(f"📚 Database Loaded: {len(players_db)} players ready.")

except Exception as e:
    print(f"❌ Critical Error loading data: {e}")
    exit()

# --- 2. STATS ENGINE ---
def get_stats(name_input):
    key = name_input.lower().strip()
    if key not in players_db:
        print(f"❌ Player '{name_input}' not found.")
        return None

    p = players_db[key]
    try:
        name = p['nickname']
        gp = int(p['games_played'])
        if gp == 0: return None
        
        gf = float(p['goals_total_for'])
        ga = float(p['goals_total_against'])
        
        # Calculate Averages
        gf_avg = gf / gp
        ga_avg = ga / gp
        total_activity = gf_avg + ga_avg
        
        return {
            "name": name,
            "gf": gf_avg,
            "ga": ga_avg,
            "total": total_activity
        }
    except ValueError:
        return None

# --- 3. ANALYSIS LOGIC (UPDATED) ---
def analyze_matchup(p1, p2):
    print("\n" + "="*50)
    print(f"⚔️  {p1['name']} vs {p2['name']}")
    print("="*50)

    # Show raw stats
    print(f"👤 {p1['name']:<12} | Score: {p1['gf']:.2f} | Concede: {p1['ga']:.2f} | Activity: {p1['total']:.2f}")
    print(f"👤 {p2['name']:<12} | Score: {p2['gf']:.2f} | Concede: {p2['ga']:.2f} | Activity: {p2['total']:.2f}")
    print("-" * 50)

    # --- NEW CALCULATION: MATCH EXPECTANCY ---
    # We take the average of both players' total activity
    expected_goals = (p1['total'] + p2['total']) / 2
    
    print(f"📊 MATCH EXPECTED GOALS: {expected_goals:.2f}")
    print("-" * 50)

    # --- STRATEGY DECISION ---
    
    # 1. UNDER 5.5 STRATEGY (The Ceiling)
    # Threshold: Expected Goals <= 3.8
    if expected_goals <= 3.8:
        print("🛡️  STRATEGY: UNDER 5.5 GOALS")
        print("   ✅ High Confidence (Defensive Match)")
        print(f"   ℹ️  Safety Margin: {5.5 - expected_goals:.2f} goals")

    # 2. OVER 1.5 STRATEGY (The Floor)
    # Threshold: Expected Goals >= 3.25
    elif expected_goals >= 3.25:
        print("🔥  STRATEGY: OVER 1.5 GOALS")
        
        if expected_goals > 4.2:
            print("   💰 GOLD MINE (High Volatility)")
        else:
            print("   ✅ Standard Safe Bet")
            
    # 3. NO BET ZONE
    else:
        print("⚠️  VERDICT: SKIP / NO BET")
        print("   ❌ Stats are too average. Unpredictable.")

# --- 4. INTERACTIVE LOOP ---
while True:
    print("\n" + "-"*30)
    print("Type player names (or 'exit' to quit)")
    
    try:
        # Player 1 Input
        p1_name = prompt("Player 1 (Home): ", completer=player_completer).strip()
        if p1_name.lower() == 'exit': break
        if not p1_name: continue
        
        player1 = get_stats(p1_name)
        if not player1: continue
        
        # Player 2 Input
        p2_name = prompt("Player 2 (Away): ", completer=player_completer).strip()
        if p2_name.lower() == 'exit': break
        if not p2_name: continue

        player2 = get_stats(p2_name)
        if not player2: continue
        
        # Run Analysis
        analyze_matchup(player1, player2)
        
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")
