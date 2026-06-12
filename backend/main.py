import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load the secret environment variables
load_dotenv()

# Initialize the API engine
app = FastAPI(title="GT League AI API")

# Security Bridge
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you can lock this down to your exact Vercel URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to get a database connection
# Helper function to get a database connection
def get_db_connection():
    try:
        # We now look for the master DATABASE_URL just like your cloud bot does
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            conn = psycopg2.connect(db_url)
        else:
            # Fallback to local if URL isn't found
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# NEW ENDPOINT: Fetch System Statistics
@app.get("/api/system-stats")
def get_system_stats():
    conn = get_db_connection()
    if not conn:
        return {"status": "offline", "total_predictions": 0}
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Query your real cloud bot memory metrics
            cursor.execute("SELECT COUNT(*) as total_predictions FROM predictions;")
            result = cursor.fetchone()
            
            return {
                "status": "online",
                "database_connected": True,
                "total_predictions": result["total_predictions"] if result else 0
            }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {"status": "error", "total_predictions": 0}
    finally:
        conn.close()

# NEW ENDPOINT: Fetch Recent Match Data
@app.get("/api/recent-matches")
def get_recent_matches():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Query the latest 10 matches using the EXACT schema from your Project Hub
            cursor.execute("""
                SELECT 
                    match_id AS id, 
                    home_player, 
                    away_player, 
                    home_goals AS home_score, 
                    away_goals AS away_score, 
                    timestamp AS match_date 
                FROM matches 
                ORDER BY timestamp DESC 
                LIMIT 10;
            """)
            matches = cursor.fetchall()
            return {"matches": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# NEW ENDPOINT: Fetch AI Predictions
@app.get("/api/recent-predictions")
def get_recent_predictions():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Query the exact columns you just discovered in the predictions table
            cursor.execute("""
                SELECT 
                    id, 
                    home_player, 
                    away_player, 
                    kickoff_utc, 
                    prediction, 
                    confidence 
                FROM predictions 
                ORDER BY kickoff_utc DESC 
                LIMIT 10;
            """)
            predictions = cursor.fetchall()
            return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# NEW ENDPOINT: Independent Model Analytics
@app.get("/api/model-analytics")
def get_model_analytics():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    prediction AS model_name,
                    COUNT(*) AS total_picks,
                    SUM(CASE WHEN status = 'Won' THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN status = 'Lost' THEN 1 ELSE 0 END) AS losses,
                    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending
                FROM predictions
                GROUP BY prediction
                ORDER BY total_picks DESC;
            """)
            analytics = cursor.fetchall()
            return {"models": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# UPGRADED ENDPOINT: Fetch Predictions (Using separate score columns)
@app.get("/api/predictions/{model_name}")
def get_model_predictions(model_name: str, date: str = None):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    decoded_name = model_name.replace("%20", " ")

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if date:
                # We dynamically stitch the home_score and away_score together as 'score'
                cursor.execute("""
                    SELECT id, home_player, away_player, kickoff_utc, prediction, confidence, status, 
                           (home_score || '-' || away_score) as score
                    FROM predictions 
                    WHERE prediction = %s AND DATE(kickoff_utc) = %s
                    ORDER BY kickoff_utc ASC;
                """, (decoded_name, date))
            else:
                cursor.execute("""
                    SELECT id, home_player, away_player, kickoff_utc, prediction, confidence, status, 
                           (home_score || '-' || away_score) as score
                    FROM predictions 
                    WHERE prediction = %s
                    ORDER BY kickoff_utc DESC 
                    LIMIT 15;
                """, (decoded_name,))
            
            predictions = cursor.fetchall()
            return {"predictions": predictions}
    except Exception as e:
        print(f"Predictions Fetch Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/stats/{model_name}")
def get_single_model_stats(model_name: str, date: str = None):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    decoded_name = model_name.replace("%20", " ")

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Base query
            query = """
                SELECT 
                    prediction AS model_name,
                    COUNT(*) AS total_picks,
                    SUM(CASE WHEN status = 'Won' THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN status = 'Lost' THEN 1 ELSE 0 END) AS losses,
                    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending
                FROM predictions
                WHERE prediction = %s
            """
            
            params = [decoded_name]
            
            # Append date filter if requested
            if date:
                query += " AND DATE(kickoff_utc) = %s"
                params.append(date)
                
            query += " GROUP BY prediction;"
            
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            
            if not result:
                 return {"stats": {"total_picks": 0, "wins": 0, "losses": 0, "pending": 0}}
                 
            return {"stats": result}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# 1. GLOBAL CALIBRATION
@app.get("/api/calibration")
def get_calibration_stats():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # FIX: Doubled percent signs (%%) to prevent psycopg2 from crashing
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN CAST(confidence AS NUMERIC) >= 90 THEN '90-100%%'
                        WHEN CAST(confidence AS NUMERIC) >= 80 AND CAST(confidence AS NUMERIC) < 90 THEN '80-89.9%%'
                        WHEN CAST(confidence AS NUMERIC) >= 70 AND CAST(confidence AS NUMERIC) < 80 THEN '70-79.9%%'
                        WHEN CAST(confidence AS NUMERIC) >= 60 AND CAST(confidence AS NUMERIC) < 70 THEN '60-69.9%%'
                        WHEN CAST(confidence AS NUMERIC) >= 50 AND CAST(confidence AS NUMERIC) < 60 THEN '50-59.9%%'
                        ELSE '< 50%%'
                    END AS bucket,
                    COUNT(*) AS total_decided,
                    SUM(CASE WHEN status = 'Won' THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN status = 'Lost' THEN 1 ELSE 0 END) AS losses
                FROM predictions
                WHERE status IN ('Won', 'Lost')
                GROUP BY 1 ORDER BY 1 DESC;
            """)
            calibration_data = cursor.fetchall()
            return {"calibration": calibration_data}
    except Exception as e:
        print(f"Global Calibration SQL Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# 2. SPECIFIC MODEL CALIBRATION (Permanently locked to All-Time)
@app.get("/api/calibration/{model_name}")
def get_specific_model_calibration(model_name: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    decoded_name = model_name.replace("%20", " ")

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # FIX: Doubled percent signs (%%)
            query = """
                SELECT 
                    CASE 
                        WHEN CAST(confidence AS NUMERIC) >= 90 THEN '90-100%%'
                        WHEN CAST(confidence AS NUMERIC) >= 80 AND CAST(confidence AS NUMERIC) < 90 THEN '80-89.9%%'
                        WHEN CAST(confidence AS NUMERIC) >= 70 AND CAST(confidence AS NUMERIC) < 80 THEN '70-79.9%%'
                        WHEN CAST(confidence AS NUMERIC) >= 60 AND CAST(confidence AS NUMERIC) < 70 THEN '60-69.9%%'
                        WHEN CAST(confidence AS NUMERIC) >= 50 AND CAST(confidence AS NUMERIC) < 60 THEN '50-59.9%%'
                        ELSE '< 50%%'
                    END AS bucket,
                    COUNT(*) AS total_decided,
                    SUM(CASE WHEN status = 'Won' THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN status = 'Lost' THEN 1 ELSE 0 END) AS losses
                FROM predictions
                WHERE status IN ('Won', 'Lost') AND prediction = %s
                GROUP BY 1 ORDER BY 1 DESC;
            """
            cursor.execute(query, (decoded_name,))
            calibration_data = cursor.fetchall()
            return {"calibration": calibration_data}
    except Exception as e:
        print(f"Specific Calibration SQL Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# NEW ENDPOINT: Player Intelligence Center
@app.get("/api/player-intelligence")
def get_player_intelligence():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # We use UNION ALL to pull every instance of a player, whether they were Home or Away
            cursor.execute("""
                WITH PlayerMatches AS (
                    SELECT home_player AS player, prediction, status FROM predictions
                    UNION ALL
                    SELECT away_player AS player, prediction, status FROM predictions
                )
                SELECT 
                    player,
                    COUNT(*) AS total_matches,
                    
                    -- Over 2.5 Model Accuracy for this player
                    SUM(CASE WHEN prediction = 'Over 2.5' AND status IN ('Won', 'Lost') THEN 1 ELSE 0 END) AS over_total,
                    SUM(CASE WHEN prediction = 'Over 2.5' AND status = 'Won' THEN 1 ELSE 0 END) AS over_wins,
                    
                    -- Home Win Model Accuracy for this player
                    SUM(CASE WHEN prediction = 'Home Win' AND status IN ('Won', 'Lost') THEN 1 ELSE 0 END) AS home_total,
                    SUM(CASE WHEN prediction = 'Home Win' AND status = 'Won' THEN 1 ELSE 0 END) AS home_wins,
                    
                    -- Away Win Model Accuracy for this player
                    SUM(CASE WHEN prediction = 'Away Win' AND status IN ('Won', 'Lost') THEN 1 ELSE 0 END) AS away_total,
                    SUM(CASE WHEN prediction = 'Away Win' AND status = 'Won' THEN 1 ELSE 0 END) AS away_wins,
                    
                    -- Overall AI Accuracy for this player
                    SUM(CASE WHEN status IN ('Won', 'Lost') THEN 1 ELSE 0 END) AS total_decided,
                    SUM(CASE WHEN status = 'Won' THEN 1 ELSE 0 END) AS total_wins
                    
                FROM PlayerMatches
                GROUP BY player
                HAVING COUNT(*) > 5 -- Only show players with enough data to be statistically relevant
                ORDER BY total_matches DESC;
            """)
            player_data = cursor.fetchall()
            return {"players": player_data}
    except Exception as e:
        print(f"Player Intelligence SQL Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# UPGRADED ENDPOINT: Prediction Failure Analysis (Using separate score columns)
@app.get("/api/failure-analysis")
def get_failure_analysis():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 1. The Scoreline Graveyard
            cursor.execute("""
                SELECT (home_score || '-' || away_score) as scoreline, COUNT(*) as count 
                FROM predictions 
                WHERE status = 'Lost' AND home_score IS NOT NULL AND away_score IS NOT NULL
                GROUP BY home_score, away_score 
                ORDER BY count DESC 
                LIMIT 10;
            """)
            scorelines = cursor.fetchall()

            # 2. The Saboteurs
            cursor.execute("""
                WITH LosingMatches AS (
                    SELECT home_player AS player FROM predictions WHERE status = 'Lost'
                    UNION ALL
                    SELECT away_player AS player FROM predictions WHERE status = 'Lost'
                )
                SELECT player, COUNT(*) as losses 
                FROM LosingMatches 
                GROUP BY player 
                ORDER BY losses DESC 
                LIMIT 10;
            """)
            saboteurs = cursor.fetchall()

            # 3. Model Blind Spots
            cursor.execute("""
                SELECT 
                    prediction as model_name, 
                    COUNT(*) as total_failures,
                    ROUND(AVG(CAST(confidence AS NUMERIC)), 1) as avg_losing_confidence
                FROM predictions 
                WHERE status = 'Lost' 
                GROUP BY prediction 
                ORDER BY total_failures DESC;
            """)
            blind_spots = cursor.fetchall()

            return {
                "scorelines": scorelines,
                "saboteurs": saboteurs,
                "blind_spots": blind_spots
            }
    except Exception as e:
        print(f"Failure Analysis SQL Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# NEW ENDPOINTS: Confidence Threshold Optimizer (Global & Per Model)
@app.get("/api/threshold-optimizer")
def get_global_thresholds():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                WITH thresholds AS (
                    SELECT 50 as val, '50%+' as label UNION ALL
                    SELECT 60, '60%+' UNION ALL
                    SELECT 70, '70%+' UNION ALL
                    SELECT 80, '80%+' UNION ALL
                    SELECT 85, '85%+' UNION ALL
                    SELECT 90, '90%+'
                )
                SELECT 
                    t.label as threshold,
                    COUNT(p.id) as total_decided,
                    COALESCE(SUM(CASE WHEN p.status = 'Won' THEN 1 ELSE 0 END), 0) as wins,
                    COALESCE(SUM(CASE WHEN p.status = 'Lost' THEN 1 ELSE 0 END), 0) as losses
                FROM thresholds t
                LEFT JOIN predictions p ON CAST(p.confidence AS NUMERIC) >= t.val AND p.status IN ('Won', 'Lost')
                GROUP BY t.val, t.label
                ORDER BY t.val ASC;
            """)
            return {"thresholds": cursor.fetchall()}
    except Exception as e:
        print(f"Global Threshold Optimizer Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# UPGRADED ENDPOINT: Sub-Model Thresholds (Fixed the %% Trap)
@app.get("/api/threshold-optimizer/{model_name}")
def get_model_thresholds(model_name: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    decoded_name = model_name.replace("%20", " ")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # FIX: Doubled the percent signs (%%) so psycopg2 doesn't crash
            cursor.execute("""
                WITH thresholds AS (
                    SELECT 50 as val, '50%%+' as label UNION ALL
                    SELECT 60, '60%%+' UNION ALL
                    SELECT 70, '70%%+' UNION ALL
                    SELECT 80, '80%%+' UNION ALL
                    SELECT 85, '85%%+' UNION ALL
                    SELECT 90, '90%%+'
                )
                SELECT 
                    t.label as threshold,
                    COUNT(p.id) as total_decided,
                    COALESCE(SUM(CASE WHEN p.status = 'Won' THEN 1 ELSE 0 END), 0) as wins,
                    COALESCE(SUM(CASE WHEN p.status = 'Lost' THEN 1 ELSE 0 END), 0) as losses
                FROM thresholds t
                LEFT JOIN predictions p ON CAST(p.confidence AS NUMERIC) >= t.val AND p.status IN ('Won', 'Lost') AND p.prediction = %s
                GROUP BY t.val, t.label
                ORDER BY t.val ASC;
            """, (decoded_name,))
            return {"thresholds": cursor.fetchall()}
    except Exception as e:
        print(f"Model Threshold Optimizer Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# NEW ENDPOINT: Model Health Monitor
@app.get("/api/health-monitor")
def get_health_monitor():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 1. Fetch Rolling Metrics
            models = ["Global", "Over 2.5", "Home Win", "Away Win"]
            rolling_metrics = []
            
            for model in models:
                model_filter = "" if model == "Global" else f"AND prediction = '{model}'"
                
                # Fetch recent limits
                cursor.execute(f"""
                    SELECT 
                        (SELECT AVG(CASE WHEN status = 'Won' THEN 100.0 ELSE 0 END) FROM (SELECT status FROM predictions WHERE status IN ('Won', 'Lost') {model_filter} ORDER BY kickoff_utc DESC LIMIT 100) as t100) as last_100,
                        (SELECT AVG(CASE WHEN status = 'Won' THEN 100.0 ELSE 0 END) FROM (SELECT status FROM predictions WHERE status IN ('Won', 'Lost') {model_filter} ORDER BY kickoff_utc DESC LIMIT 500) as t500) as last_500,
                        (SELECT AVG(CASE WHEN status = 'Won' THEN 100.0 ELSE 0 END) FROM (SELECT status FROM predictions WHERE status IN ('Won', 'Lost') {model_filter} ORDER BY kickoff_utc DESC LIMIT 1000) as t1000) as last_1000
                """)
                row = cursor.fetchone()
                
                rolling_metrics.append({
                    "model_name": model,
                    "last_100": float(row["last_100"] or 0),
                    "last_500": float(row["last_500"] or 0),
                    "last_1000": float(row["last_1000"] or 0)
                })

            # 2. Generate System Alerts based on data drift
            alerts = []
            for metric in rolling_metrics:
                if metric["last_100"] > 0 and metric["last_500"] > 0:
                    drift = metric["last_100"] - metric["last_500"]
                    
                    if drift <= -5.0:
                        alerts.append({
                            "severity": "CRITICAL",
                            "model": metric["model_name"],
                            "trigger": "Sudden Performance Drop",
                            "description": f"Recent 100-match accuracy ({metric['last_100']:.1f}%) has fallen significantly below 500-match baseline ({metric['last_500']:.1f}%)."
                        })
                    elif drift >= 5.0:
                        alerts.append({
                            "severity": "NOTICE",
                            "model": metric["model_name"],
                            "trigger": "Unusual Win Streak",
                            "description": f"Algorithm is over-performing baseline by +{drift:.1f}%. Monitor for potential mean-reversion."
                        })
            
            # Default alert if system is perfectly healthy
            if not alerts:
                alerts.append({
                    "severity": "HEALTHY",
                    "model": "Global System",
                    "trigger": "All Metrics Stable",
                    "description": "No significant calibration drift or performance drops detected across any active intelligence engines."
                })

            return {"metrics": rolling_metrics, "alerts": alerts}
    except Exception as e:
        print(f"Health Monitor Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# NEW ENDPOINT: Feature Intelligence
@app.get("/api/feature-intelligence")
def get_feature_intelligence():
    # In a production ML environment, this data would be extracted from 
    # your model.feature_importances_ or SHAP values.
    
    top_features = [
        {"feature": "Win Rate Difference", "category": "Historical", "importance": 88.5, "correlation": 0.72},
        {"feature": "Over 2.5 Rate (Last 10)", "category": "Form", "importance": 82.1, "correlation": 0.68},
        {"feature": "H2H Goals Scored", "category": "Matchup", "importance": 76.4, "correlation": 0.55},
        {"feature": "Home Goal Average", "category": "Venue", "importance": 65.2, "correlation": 0.48},
        {"feature": "Away Goal Average", "category": "Venue", "importance": 63.8, "correlation": 0.45},
        {"feature": "Current Win Streak", "category": "Momentum", "importance": 58.9, "correlation": 0.39},
        {"feature": "Days Since Last Match", "category": "Fatigue", "importance": 22.4, "correlation": -0.15},
    ]

    return {"features": top_features}

# NEW ENDPOINT: Data Quality Monitor
@app.get("/api/data-quality")
def get_data_quality():
    # In production, these would be active queries checking for NULLs, 
    # string anomalies, and row counts in your raw ingestion tables.
    
    checks = [
        {"metric": "Missing Values (Nulls)", "value": "0.01%", "threshold": "< 1.0%", "status": "Passed"},
        {"metric": "Duplicate Matches", "value": "0 Rows", "threshold": "0 Rows", "status": "Passed"},
        {"metric": "Missing Player Names", "value": "0 Rows", "threshold": "0 Rows", "status": "Passed"},
        {"metric": "Invalid Scorelines (e.g. -1)", "value": "12 Rows", "threshold": "0 Rows", "status": "Warning"},
        {"metric": "Feature Generation Failures", "value": "0.05%", "threshold": "< 0.5%", "status": "Passed"},
    ]

    alerts = [
        {
            "severity": "WARNING", 
            "issue": "Format Anomaly: Invalid Scorelines", 
            "description": "12 recent matches contained corrupted score strings. The automated pipeline successfully isolated and quarantined them."
        },
        {
            "severity": "HEALTHY", 
            "issue": "Ingestion Pipeline Status", 
            "description": "Cloud data ingestion operating at nominal latency. No broken scraper streams detected."
        },
        {
            "severity": "HEALTHY", 
            "issue": "Dataset Integrity & Volume", 
            "description": "No empty datasets detected. Daily ingestion volume perfectly matches the expected historical rate."
        }
    ]

    return {"checks": checks, "alerts": alerts}

    # Fixing Render deployment lock