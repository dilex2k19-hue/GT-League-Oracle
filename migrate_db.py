import psycopg2
import psycopg2.extras

# 1. Connect to your Local Database (Source)
print("🔌 Connecting to Local Database...")
local_conn = psycopg2.connect(dbname="gt_league_db", user="postgres", password="admin123", host="localhost")
local_cursor = local_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# 2. Connect to your Supabase Cloud Database (Destination)
print("☁️ Connecting to Cloud Database...")
SUPABASE_URL = "postgresql://postgres.wzziydbnbjpfoxxwevog:behumble250%40@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"
cloud_conn = psycopg2.connect(SUPABASE_URL)
cloud_cursor = cloud_conn.cursor()

# 3. Pull data from Local
print("📦 Extracting historical matches from laptop...")
local_cursor.execute("SELECT home_player, away_player, home_goals, away_goals, winner, over25, timestamp FROM matches;")
matches = local_cursor.fetchall()
print(f"✅ Found {len(matches)} historical matches.")

# 4. Create the Table in the Cloud
print("🏗️ Building 'matches' table in the Cloud...")
cloud_cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id SERIAL PRIMARY KEY,
        home_player VARCHAR(50),
        away_player VARCHAR(50),
        home_goals INTEGER,
        away_goals INTEGER,
        winner VARCHAR(10),
        over25 BOOLEAN,
        timestamp TIMESTAMP
    );
""")
cloud_conn.commit()

# 5. Upload data to Cloud
print("🚀 Uploading data to Supabase (This might take 10-20 seconds)...")
insert_query = """
    INSERT INTO matches (home_player, away_player, home_goals, away_goals, winner, over25, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

# Prepare the data efficiently
data_to_insert = [(m['home_player'], m['away_player'], m['home_goals'], m['away_goals'], m['winner'], m['over25'], m['timestamp']) for m in matches]

# Execute batch insert
psycopg2.extras.execute_batch(cloud_cursor, insert_query, data_to_insert)
cloud_conn.commit()

print("🎉 Migration Complete! The Oracle now has its memory in the cloud.")

# Close connections
local_cursor.close()
local_conn.close()
cloud_cursor.close()
cloud_conn.close()