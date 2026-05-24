import psycopg2
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------
# 1. LOAD THE DATA
# ---------------------------------------------------------
def load_data():
    print("🔌 Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        dbname="gt_league_db",
        user="postgres",
        password="admin123",
        host="localhost"
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM match_features;")
    
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    
    cursor.close()
    conn.close()
    
    return df

# ---------------------------------------------------------
# 2. TRAIN THE SPECIALISTS
# ---------------------------------------------------------
def train_specialists(df):
    print(f"📥 Loaded {len(df)} historical matches.")
    df = df.fillna(0)
    
    # 1. Define the Front of the flashcard (The Features)
    drop_cols = ['match_id', 'timestamp', 'home_player', 'away_player', 
                 'target_home_win', 'target_away_win', 'target_over25']
    X = df.drop(columns=drop_cols)
    
    # 2. Define our 3 Specialist Targets and their filenames
    targets = {
        'target_home_win': 'rf_home_model.pkl',
        'target_away_win': 'rf_away_model.pkl',
        'target_over25': 'rf_over25_model.pkl'
    }
    
    os.makedirs('models', exist_ok=True)
    scaler_saved = False
    
    # 3. Train a dedicated AI for each target
    for target_col, filename in targets.items():
        print(f"\n=====================================")
        print(f"🚀 TRAINING SPECIALIST: {target_col.upper()}")
        print(f"=====================================")
        
        y = df[target_col]
        
        # Split Data (80% Train, 20% Test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        # Scale Data (We only need to save the scaler once!)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        if not scaler_saved:
            joblib.dump(scaler, 'models/scaler.pkl')
            scaler_saved = True
            
        # Train the Disciplined Random Forest
        model = RandomForestClassifier(n_estimators=200, max_depth=7, min_samples_leaf=10, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Take the Final Exam
        predictions = model.predict(X_test_scaled)
        acc = accuracy_score(y_test, predictions)
        
        # For Precision, we use zero_division=0 just in case the AI refuses to guess
        prec = precision_score(y_test, predictions, zero_division=0) 
        
        print(f"Accuracy:  {acc * 100:.2f}%")
        print(f"Precision: {prec * 100:.2f}%")
        
        # Save this specific AI's brain
        joblib.dump(model, f'models/{filename}')
        print(f"✅ Saved to models/{filename}")

    print("\n🎉 All 3 Specialist Models have been successfully trained and saved!")

if __name__ == "__main__":
    df = load_data()
    train_specialists(df)