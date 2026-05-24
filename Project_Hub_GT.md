# GT LEAGUE AI PREDICTION SYSTEM HUB

---

# PROJECT OVERVIEW

## Project Name
GT League AI Prediction System

## Main Goal
Build an AI-powered GT League prediction system capable of predicting:
- Home Win
- Away Win
- Over 2.5 Goals

The system will:
- scrape GT League statistics,
- analyze player performance,
- track historical patterns,
- generate probability-based predictions,
- and select the best 2 matches every hour.

---

# CORE OBJECTIVES

## Primary Objectives
- Build reliable GT League data scraper
- Collect historical match data automatically
- Build player statistics engine
- Train prediction models
- Filter only high-confidence predictions
- Create dashboard for monitoring

## Secondary Objectives
- Detect hidden statistical patterns
- Analyze odds movement
- Build automated alerts
- Create ROI tracking system
- Build self-improving prediction engine

---

# SYSTEM ARCHITECTURE

```text
                ┌─────────────────────┐
                │   GT LEAGUES SITE   │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │      SCRAPER        │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │      DATABASE       │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   FEATURE ENGINE    │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │     ML MODELS       │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ PREDICTION FILTER   │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │      DASHBOARD      │
                └─────────────────────┘
```

---

# TECHNOLOGY STACK

## Scraping
- Python
- Playwright
- BeautifulSoup
- Asyncio

## Database
- PostgreSQL 

## AI / Machine Learning
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- LightGBM

## Backend
- FastAPI

## Dashboard
- Streamlit
- Flask (Optional)

## Version Control
- Git
- GitHub

---

# PROJECT PHASES

---

# Phase 1: Environment Setup

## Goal
Prepare development environment.

## Tasks
- [x] Install Python
- [x] Create virtual environment
- [x] Install required libraries (`requests`, `psycopg2`)
- [x] Setup VSCode
- [x] Setup GitHub repository
- [x] Setup project folder structure

## Notes & Observations
- **Environment Context:** Successfully running on a Linux OS (Ubuntu) with the project isolated inside a dedicated Python virtual environment `(venv)`.
- **Bug Encountered:** Script threw `ModuleNotFoundError: No module named 'requests'`.
- **Fix Applied:** Recognized that the virtual environment is a blank slate by design. Executed `pip install requests` strictly within the active `(venv)` to resolve the dependency gap.

## Status
COMPLETE ✅


# Phase 2: GT League Investigation

## Goal
Understand GT League website structure.

## Tasks
- [x] Investigate website structure
- [x] Inspect Network requests
- [x] Detect APIs (Found `api/fixtures`)
- [x] Identify hidden endpoints (JSON payloads directly accessible)
- [x] Identify anti-bot protections (Encountered HTTP 451, bypassed via headers)
- [x] Inspect statistics pages
- [x] Investigate Head-to-Head section

## Expected Outputs
- **API endpoints:** Mapped the hidden `https://api.gtleagues.com/api/fixtures` endpoint, utilizing `kickoff`, `limit`, `offset`, and `status` parameters.
- **Match data structure:** Cleanly mapped from the JSON payload (`match_id` -> `id`, `timestamp` -> `kickoff`, etc.).
- **Player statistics structure:** Located deep within the nested JSON (`participants -> participant -> player -> nickname`).
- **H2H data structure:** Extracted home/away mapping and exact scores from the `result -> stats` object.

## Notes & Observations
- **Major Discovery:** The website data is delivered in a clean JSON format via a hidden API. This allowed us to pivot away from slow, messy HTML browser automation (Playwright/BeautifulSoup) to incredibly fast, direct API calls using Python's `requests` library.
- **Anti-Bot System:** The site initially threw an `HTTP 451 Unavailable For Legal Reasons` error. We successfully diagnosed this not as a strict geo-block, but as an anti-bot filter checking for standard browser trust headers. Injecting elite browser-emulating headers (`Origin`, `Referer`, `User-Agent`) successfully bypassed the filter without requiring a VPN proxy.

## Status
COMPLETE ✅


# Phase 3: Scraper Development

## Goal
Build reliable GT League scraper.

## Tasks
- [x] Build first scraper (Pivoted from Playwright to Python `requests` API scraper)
- [ ] Scrape scheduled matches (Deferred: Currently focusing on historical data)
- [x] Scrape finished matches
- [x] Scrape player statistics (Raw match data captured; exact stats calculated via SQL in Phase 6)
- [ ] Scrape standings (Deferred)
- [x] Scrape H2H data (Raw match data captured; exact H2H calculated via SQL in Phase 6)
- [x] Handle pagination (Optimized payload to `limit=100` based on UI dropdown discovery)
- [x] Handle anti-bot systems (Bypassed 451 block by injecting elite browser trust headers)
- [x] Create automated scraping loop (Built the "Historical Harvester" script)

## Target Data
- [x] Match results
- [x] Scores
- [x] Player stats (Calculated downstream)
- [x] Over 2.5 results (Calculated downstream)
- [x] Win/Loss ratios (Calculated downstream)
- [ ] Rankings
- [x] H2H history (Calculated downstream)

## Notes & Observations
- **Major Architecture Pivot:** Because of the Phase 2 API discovery, we skipped building a heavy Playwright browser simulator. The resulting `requests` script is significantly faster, less prone to breaking when the website UI updates, and uses a fraction of the system memory.
- **Optimization Win:** Discovered the API accepts `limit=100` (instead of 50), which cut our required network requests in half and drastically sped up the harvesting process while lowering the risk of IP bans.

## Status
COMPLETE ✅

---

# Phase 4: Database System

## Goal
Store and organize scraped data.

## Tasks
- [x] Setup database (Pivoted from SQLite to PostgreSQL for production-grade scale)
- [x] Create matches table
- [x] Create players table
- [x] Create H2H table
- [ ] Create standings table (Deferred)
- [ ] Create predictions table (Deferred: Will build when AI outputs predictions)
- [x] Build database insertion functions (Handled JSON parsing and on-the-fly feature calculations like `over25` and `winner`)
- [x] Build database query functions

## Notes & Observations
- **Architecture Pivot:** Upgraded the planned SQLite database to PostgreSQL (`gt_league_db`) to handle the massive 20,000+ row count and allow for advanced SQL aggregations later on.
- **Data Pipeline:** Engineered `db_manager.py` to seamlessly parse the nested API JSON into clean relational tables. It includes duplicate protection (`ON CONFLICT (match_id) DO NOTHING`) and validation logic to skip voided or incomplete matches.
- **Bug Encountered:** Script threw `psycopg2.errors.InsufficientPrivilege: permission denied for schema public` during table creation.
- **Fix Applied:** Identified this as a PostgreSQL 15+ default security feature. Logged in directly to the database as the superuser and ran `GRANT ALL ON SCHEMA public TO gt_admin;` to authorize our script.

## Status
COMPLETE ✅

# Phase 5: Historical Data Collection

## Goal
Collect large amount of historical data.

## Tasks
- [x] Collect first 1000 matches
- [x] Collect first 5000 matches
- [x] Collect player histories (Automated via Historical Harvester script)
- [x] Validate data quality (Insertion logic automatically skipped voided/incomplete matches)
- [x] Remove duplicate matches (Handled via PostgreSQL `ON CONFLICT (match_id) DO NOTHING`)
- [x] Fix corrupted data (Handled during the JSON parsing phase)

## Minimum Dataset Goal
20,000+ matches (ACHIEVED: 20,115 matches safely stored)

## Notes & Observations
- **Automation Tool:** Engineered `harvester.py` to use Python's `datetime` module, looping backwards day-by-day and streaming API data directly into PostgreSQL.
- **Optimization Win:** Adjusted the pagination payload to `limit=100` based on UI dropdown discovery. This cut the total extraction time for 65 days of historical data from 15+ minutes down to under 9 minutes, drastically reducing server load and ban risk.
- **Dataset Secured:** Successfully secured 20,115 clean match records, perfectly setting the stage for machine learning.

## Status
COMPLETE ✅


### Phase 6: Feature Engineering

**Goal:** Create time-aware, predictive features without temporal data leakage.

**Features Built:**
* **Rolling Form Features (Time-Aware):** Last 10 matches win rate, draw rate, loss rate, avg goals scored/conceded, Over 2.5 frequency.
* **Split Features:** Home-specific performance and Away-specific performance.
* **Streak & Consistency Features:** Current win streaks, Over 2.5 streaks, scoring consistency (scored in L5), and clean sheet rate (L10).
* **Volume & Fatigue Features:** Matches played exactly today, in the last 24 hours, and in the last 7 days.
* **Head-to-Head (H2H):** All-time shared H2H stats and Recent H2H (Last 5 meetings).
* **Comparative Features (Differences):** Win rate difference, goal average difference, and Over 2.5 rate difference.

**Data Infrastructure:**
* Built `snapshot_builder.py` (The Engine) to loop through matches in perfect chronological order.
* Built `feature_calculators.py` (The Math Lab) to cleanly separate the complex calculation logic.
* Successfully generated and bulk-inserted 20,115 historical feature snapshots into the PostgreSQL `match_features` table.

**Status:** ✅ COMPLETED

---

## Phase 7: AI / Machine Learning

### Goal
Train highly precise prediction models using historical GT League data to forecast match outcomes.

### Prediction Targets
- [x] Home Win
- [x] Away Win
- [x] Over 2.5 Goals

### Models Tested & Selected
- **Random Forest:** ✅ **(Selected & Tuned)** Built 3 highly-tuned specialist models (`n_estimators=200`, `max_depth=7`, `min_samples_leaf=10`).
- **Logistic Regression:** (Tested as an initial baseline; discarded due to linear limitations).
- **XGBoost / LightGBM:** (Bypassed for now, as Random Forest comfortably hit our target precision metrics).

### Tasks
- [x] Prepare datasets (Loaded 20,115 snapshots from PostgreSQL & applied `StandardScaler`)
- [x] Split train/test data (80/20 chronological split, `shuffle=False` to strictly prevent time leakage)
- [x] Train baseline models (Initial models showed overfitting and high variance)
- [x] Evaluate accuracy (Analyzed feature importance: realized Goal Differential heavily outweighs raw Win Rate)
- [x] Tune hyperparameters (Disciplined the trees to cap depth and require minimum sample leaves)
- [x] Save best models (Serialized and exported 3 `.pkl` models and 1 `.pkl` scaler to the `models/` directory)

### Final Metrics Achieved
- **Home Win Specialist:** Accuracy: 63.06% | Precision: 59.56%
- **Away Win Specialist:** Accuracy: 59.28% | Precision: 60.22%
- **Over 2.5 Specialist:** Accuracy: 75.39% | Precision: 77.08%

### Status
✅ COMPLETED

---

# Phase 8: Prediction Filtering System

## Goal
Select only elite predictions by scanning the live upcoming schedule.

## Filtering Rules
- [x] Confidence threshold (Sorts by highest AI probability)
- [x] Time window filtering (Strictly targets matches kicking off in the next 45 minutes)
- [x] Status validation (Filters out "Live" matches [status: 1], targets only "Not Started" [status: 0])

## Tasks
- [x] Build confidence scoring (Extracted exact probabilities using `.predict_proba()`)
- [x] Build ranking engine (Sorted the array of dictionaries by confidence score)
- [x] Select best 2 predictions hourly (Sliced the top 2 highest-value setups)
- [x] Handle feature alignment (Built an automated aligner using `scaler.feature_names_in_` to prevent pipeline crashes)

## Status
✅ COMPLETED

---

# Phase 9: Dashboard Development

## Goal
Visualize predictions and statistics.

## Dashboard Features
- Live predictions
- Player rankings
- Match statistics
- Prediction history
- ROI tracking
- Accuracy tracking

## Tasks
- [ ] Build dashboard UI
- [ ] Connect database
- [ ] Display live predictions
- [ ] Display statistics charts
- [ ] Build filters

## Status
NOT STARTED

---

# Phase 10: Automation & Alerts

## Goal
Automate the prediction workflow to run autonomously and report directly to mobile.

## Tasks
- [x] Automate scraping (Integrated API scanner directly into a continuous background loop)
- [x] Automate model predictions (Connected the 3 Scikit-Learn Specialist models to the live data feed)
- [x] Schedule hourly predictions (Created a built-in sleep timer to scan the market every 30 minutes)
- [x] Build Telegram alerts (Deployed the `@GTLeagueOracle_bot` to push formatted alerts to mobile)
- [x] Build prediction logging (Created a `predictions` table in PostgreSQL to act as the bot's memory)
- [x] Build automatic feedback loop (Engineered the bot to scan finished matches, grade its past predictions, and report Wins/Losses)

## Status
✅ COMPLETED

---

# DATABASE STRUCTURE

## Matches Table

| Column | Description |
|---|---|
| match_id | Unique match ID |
| home_player | Home player |
| away_player | Away player |
| home_goals | Goals scored by home |
| away_goals | Goals scored by away |
| over25 | Over 2.5 result |
| winner | Match winner |
| timestamp | Match time |

---

## Players Table

| Column | Description |
|---|---|
| player_id | Unique player ID |
| player_name | Player name |
| win_rate | Win percentage |
| avg_goals | Average goals scored |
| avg_conceded | Average goals conceded |
| over25_rate | Over 2.5 frequency |

---

## H2H Table

| Column | Description |
|---|---|
| playerA | First player |
| playerB | Second player |
| matches_played | Total H2H matches |
| playerA_wins | Wins by playerA |
| avg_goals | Average goals |
| over25_rate | Over 2.5 frequency |

---

# CURRENT PRIORITIES

## Immediate Focus
1. Investigate GT League website
2. Build first scraper
3. Save first match data
4. Setup database
5. Start collecting history

---

# CURRENT TASK

```text
Current Task:
Investigate GT League website structure and identify data sources.
```

---

# BUG JOURNAL

## Format

```text
BUG:
Description of bug

CAUSE:
Root cause

FIX:
How it was solved
```

---

# EXPERIMENT LOG

## Format

```text
Experiment:
What was tested

Result:
Outcome of experiment

Conclusion:
Was it useful?
```

---

# MODEL PERFORMANCE TRACKER

| Model | Target | Accuracy | ROI | Notes |
|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A |

---

# DAILY OBSERVATIONS

## Format

```text
Observation:
Interesting pattern noticed

Possible Meaning:
Potential edge or explanation
```

---

# FUTURE IDEAS

- [ ] Odds movement tracking
- [ ] Telegram alerts
- [ ] Automatic betting integration
- [ ] Player fatigue analysis
- [ ] AI confidence explanations
- [ ] Pattern anomaly detection
- [ ] Multi-league support

---

# GEMINI AI PROJECT ASSISTANT

## Gemini Role Prompt

```text
You are a senior AI engineer helping build a GT League prediction system.

Your responsibilities:
- guide project architecture,
- prevent overengineering,
- explain concepts simply,
- debug scraper issues,
- assist with ML pipelines,
- maintain project organization,
- update project documentation,
- help identify profitable statistical patterns,
- keep development structured and realistic.

The project focuses on:
- GT League match prediction,
- Over 2.5 prediction,
- Home/Away win prediction,
- statistical analysis,
- automated scraping,
- machine learning,
- and betting market behavior.

Always prioritize:
- simplicity,
- reliability,
- scalability,
- and practical implementation.
```

---

# DEVELOPMENT RULES

## Important Rules
- Focus on one phase at a time
- Never rush into AI before collecting enough data
- Prioritize scraper reliability
- Track every bug and fix
- Save all experiments
- Keep system modular
- Avoid overengineering early

---

# FIRST MAJOR MILESTONE

```text
Successfully scrape and store GT League match results automatically.
```

---

# LONG-TERM VISION

Build a fully automated AI prediction platform capable of:
- identifying high-probability GT League outcomes,
- detecting profitable statistical patterns,
- filtering elite predictions,
- and maintaining long-term prediction consistency.