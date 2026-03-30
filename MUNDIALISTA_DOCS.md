# MUNDIALISTA AI - Complete Documentation

## Project Overview

Mundialista AI is an international football (soccer) match prediction system
that combines statistical modeling with real-world football data to generate
win/draw/loss probabilities, expected goals, likely scorelines, and match insights
for any pairing of national teams worldwide.

**Core Technology:**
- Dixon-Coles adjusted Poisson regression model
- Monte Carlo simulation (10,200 iterations per prediction)
- Bayesian shrinkage estimation for attack/defense ratings
- Time-weighted form analysis with tournament importance
- Auto-derived star player detection from 47,000+ goal records
- Head-to-head historical analysis

**Coverage:**
- 200+ national teams
- 49,000+ historical international matches
- 47,000+ individual goal records
- FIFA rankings integration
- Real-time recent results overlay

---

## Architecture & File Struct
mundialista-ai/
|-- app.py # Streamlit web UI (main app)
|-- prediction_engine.py # Core prediction engine v6.2
|-- chart_generator.py # Visual analytics chart generation
|-- match_manager.py # CLI tool for managing data + predictions
|-- requirements.txt # Python dependencies
|-- .streamlit/
| |-- config.toml # Streamlit theme + server config
|-- data/
| |-- results.csv # Historical match results (49,000+)
| |-- rankings.csv # FIFA world rankings
| |-- goalscorers.csv # Individual goal records (47,000+)
| |-- recent_results.csv # User-added recent match results
| |-- recent_goalscorers.csv # User-added recent goal records
|-- charts/ # Generated chart images (auto-created)
|-- prediction_engine_v6_backup.py # Engine backup
|-- app_v6_backup.py # UI backup
|-- test_v61.py # Quick test script
|-- patch_*.py # Various patch scripts (reference)

text

---

## How the Prediction Engine Works

### Step 1: Data Loading
The engine loads three datasets on startup:
- results.csv + recent_results.csv (merged automatically)
- rankings.csv
- goalscorers.csv + recent_goalscorers.csv (merged automatically)

Caching ensures data is only loaded once per session.
Call clear_cache() to force reload after adding new data.

### Step 2: Team Statistics (get_team_stats)
For each team, the engine analyzes the last 20 matches:
- Calculates goals scored (GF) and goals conceded (GA)
- Applies TIME DECAY: recent matches count more (decay rate 0.003)
- Applies TOURNAMENT WEIGHTS:
  * FIFA World Cup: 1.0 (full weight)
  * Copa America / UEFA Euro: 0.9
  * Nations League / AFCON / AFC: 0.85
  * World Cup Qualification: 0.8
  * Friendly: 0.5
- Applies OPPONENT STRENGTH: goals vs top teams count more
- Uses BAYESIAN SHRINKAGE: small samples pulled toward global mean
  * Global average: 1.36 goals per match
  * Shrinkage factor K=8

Output: attack rating and defense rating (1.0 = average)

### Step 3: Lambda Calculation (predict)
Lambda = expected goals for each team in this specific matchup.

Formula:
  lambda_form = attack_rating * opponent_defense * global_average
  lambda_rank = global_average * (rank_factor_a / rank_factor_b)
  lambda_final = rank_weight * lambda_rank + form_weight * lambda_form

Rank weights:
  - Both teams in top 30: 30% ranking, 70% form
  - Otherwise: 20% ranking, 80% form

### Step 4: Modifiers Applied
1. STAR PLAYERS: Auto-derived from goalscorers.csv + manual overrides
   - Top scorers per team identified (min 4 goals, min 0.20 gpm)
   - Diminishing returns: 1st star 55%, 2nd 42%, 3rd 34%
   - Cap: 1.25x maximum boost
   - Relative boost: normalized so both teams dont just inflate

2. HEAD-TO-HEAD: Last 8 meetings analyzed
   - Win rate difference creates +/- 5% lambda adjustment
   - Example: 6-1-1 record = +3.1% for dominant team

3. HOME ADVANTAGE: 
   - Home team: lambda * 1.06
   - Away team: lambda * 0.94
   - Neutral venue: no adjustment

4. MAX RATIO CAP: For top-30 matchups, max lambda ratio is 1.40
   - Prevents unrealistic blowout predictions in elite clashes

### Step 5: Score Matrix (Dixon-Coles)
- Independent Poisson probabilities for each scoreline (0-0 to 8-8)
- Dixon-Coles correction (rho = -0.08):
  * Reduces 0-0 probability slightly
  * Reduces 0-1 and 1-0 slightly
  * REDUCES 1-1 probability (key fix for elite matches)
  * Leaves 2+ goal scorelines unchanged
- Matrix normalized to sum to 100%

### Step 6: Output
- Win/Draw/Loss percentages
- Expected goals (lambda) per team
- Top 10 most likely scorelines with simulation counts
- Match type classification
- Star player lists with boost values
- Head-to-head record
- Monte Carlo goal distributions

---

## Features List

### Prediction Engine
- [x] Dixon-Coles Poisson model
- [x] Monte Carlo simulation (10,200 runs)
- [x] Time-weighted form analysis
- [x] Tournament importance weighting
- [x] Opponent strength adjustment
- [x] Bayesian shrinkage estimation
- [x] FIFA ranking integration
- [x] Auto-derived star players from goalscorer data
- [x] Manual star player overrides (25+ teams covered)
- [x] Name normalization (accent handling, Jr/Junior dedup)
- [x] Head-to-head historical analysis (last 8 meetings)
- [x] Home/away/neutral venue adjustment
- [x] Match type classification (Elite/Competitive/Favorite/Mismatch)

### Web UI (Streamlit)
- [x] 2000s retro neon dark theme
- [x] Team selector with 200+ nations
- [x] Win probability bars (cyan/gold/pink)
- [x] Expected goals display
- [x] Top scorelines with crown for most likely
- [x] Star player cards with boost values
- [x] Head-to-head visualization bar
- [x] Match type badges (animated pulse for Elite Clash)
- [x] AI-generated match insight text
- [x] 5 chart tabs (Summary, Win Prob, Matrix, Scores, Goals)
- [x] HTML report download
- [x] Raw JSON data expander
- [x] Scrolling marquee banner

### Sidebar Admin Panel
- [x] Add recent match results
- [x] View recent results list
- [x] Card predictor (yellow/red forecast)
- [x] Clear recent data button
- [x] Auto cache refresh on data changes

### CLI Match Manager (match_manager.py)
- [x] Interactive menu system
- [x] Add match results with guided input
- [x] Add goalscorers with penalty/own goal flags
- [x] Delete results (with associated goals cleanup)
- [x] Quick predict from command line
- [x] Card prediction
- [x] View all recent data

### Data System
- [x] Auto-merge recent_results.csv with historical data
- [x] Auto-merge recent_goalscorers.csv with historical data
- [x] Deduplication on merge
- [x] Date sorting on merge
- [x] Cache invalidation on data changes

---

## How to Use - Streamlit UI

### Starting the App
cd mundialista-ai
streamlit run app.py

text
Opens at http://localhost:8501

### Making a Prediction
1. Select Team A from the dropdown (home team)
2. Select Team B from the dropdown (away team)
3. Check/uncheck "Neutral venue" checkbox
4. Click the orange "PREDICT" button
5. Wait 2-3 seconds for results

### Reading the Results
- TOP SECTION: Three metric boxes showing Win% for each team + Draw%
- PROBABILITY BARS: Visual bars (cyan = Team A, gold = Draw, pink = Team B)
- STAR PLAYERS: Two side-by-side cards showing key players + boost factor
- HEAD-TO-HEAD: Color bar showing win/draw/loss split from last 8 meetings
- EXPECTED GOALS: Lambda values (higher = more goals expected)
- TOP SCORES: Most likely scorelines (gold crown = #1 most likely)
- AI INSIGHT: Text summary of match dynamics
- VISUAL ANALYTICS: 5 tabs with generated charts

### Sidebar Features
Click the ">" arrow on the left to open sidebar:

ADD RECENT RESULT:
  - Enter date, teams, scores, tournament
  - Click Save to add to database
  - Engine automatically includes in next prediction

VIEW RECENT RESULTS:
  - Shows all manually added results
  - Color coded with dates and tournaments

CARD PREDICTOR:
  - Select two teams
  - Shows expected yellows per team
  - Shows red card probability with risk level

CLEAR RECENT DATA:
  - Removes all manually added results and goals
  - Resets to base historical data only

---

## How to Use - CLI Match Manager

### Starting the CLI
python match_manager.py

text

### Menu Options

OPTION 1 - Show Recent Results:
  Displays all manually added matches and goals.

OPTION 2 - Add Match Result:
  Interactive prompts:
  - Date (YYYY-MM-DD format, Enter for today)
  - Home team name (must match database spelling)
  - Away team name
  - Scores
  - Tournament (numbered list or custom)
  - City/Country (optional)
  - Neutral venue flag
  - Then optionally add goalscorers

OPTION 3 - Add Goals:
  For adding goals to an already-entered match.
  Format: PlayerName Minute Team
  Example: Gyokeres 15 Sweden
  Add (P) for penalty: Messi 45 Argentina (P)
  Add (OG) for own goal: Smith 67 England (OG)
  Type "done" when finished.

OPTION 4 - Delete Result:
  Shows numbered list of recent results.
  Enter index to delete. Associated goals auto-removed.

OPTION 5 - Quick Predict:
  Enter two team names for instant prediction output.
  Shows: percentages, lambdas, stars, H2H, top scorelines.

OPTION 6 - Card Prediction:
  Enter two teams for yellow/red card forecast.
  Based on defensive aggression and match intensity.

OPTION 7 - Exit

### Team Name Spelling
Team names must match the database exactly. Common formats:
  - "United States" (not "USA" or "US")
  - "South Korea" (not "Korea Republic")
  - "China PR" (not "China")
  - "Ivory Coast" (not "Cote d Ivoire")

---

## How to Add Recent Results

### Why Add Recent Results?
The base dataset may not include the latest matchday.
Adding recent results improves prediction accuracy by:
- Updating team form ratings
- Adding new goalscorer data for star detection
- Reflecting latest head-to-head results

### Method 1: Streamlit Sidebar
1. Open sidebar
2. Expand "Add Recent Result"
3. Fill in all fields
4. Click Save
5. Predictions automatically update

### Method 2: CLI Match Manager
1. Run: python match_manager.py
2. Choose option 2
3. Follow prompts
4. Goals can be added in same session

### Method 3: Direct CSV Edit
Edit data/recent_results.csv directly:
date,home_team,away_team,home_score,away_score,tournament,city,country,neutral
2026-03-20,Sweden,Ukraine,3,0,FIFA World Cup qualification,Stockholm,Sweden,False

text

Edit data/recent_goalscorers.csv:
date,home_team,away_team,team,scorer,minute,own_goal,penalty
2026-03-20,Sweden,Ukraine,Sweden,Viktor Gyokeres,15,False,False

text

### Important Notes
- Team names must match database spelling exactly
- Date format: YYYY-MM-DD
- After manual CSV edit, restart app or call clear_cache()
- Duplicate matches (same date + teams) are auto-deduplicated

---

## How to Deploy

### Streamlit Cloud (Recommended)
1. Push all code to GitHub
2. Go to share.streamlit.io
3. Click "New app"
4. Select repository: mundialista-ai
5. Branch: main
6. Main file: app.py
7. Click Deploy
8. Wait 2-3 minutes for build
9. App is live at [your-username].streamlit.app

### Requirements for Deployment
- requirements.txt must list all dependencies
- All data files must be committed to git
- No local file paths (all paths are relative)
- .streamlit/config.toml for theme settings

### Local Deployment
pip install -r requirements.txt
streamlit run app.py

text

---

## Configuration & Tuning Guide

### Key Parameters (in prediction_engine.py CONFIG dict)

SCORING MODEL:
  GLOBAL_GF: 1.36        # Global average goals per match
  GLOBAL_GA: 1.36        # Should equal GLOBAL_GF
  SHRINK_K: 8            # Bayesian shrinkage strength (higher = more conservative)
  LAST_N_MATCHES: 20     # Form window size

WEIGHTING:
  DECAY_RATE: 0.003      # Time decay (higher = recent matches matter more)
  HOME_ADVANTAGE: 1.06   # Home team lambda multiplier
  AWAY_DISADVANTAGE: 0.94 # Away team lambda multiplier
  RANK_WEIGHT_TOP: 0.30  # Ranking influence for top-30 matchups
  RANK_WEIGHT_OTHER: 0.20 # Ranking influence for other matchups

CONSTRAINTS:
  TOP_TEAM_THRESHOLD: 30  # Rank cutoff for "top team" logic
  MAX_RATIO: 1.40         # Maximum lambda ratio in elite matches

DIXON-COLES:
  DIXON_COLES_RHO: -0.08  # Score correlation correction
    # More negative = stronger 1-1 suppression
    # Range: -0.03 (weak) to -0.12 (very strong)

STAR PLAYERS:
  STAR_MIN_GOALS: 4        # Minimum goals to qualify as auto-star
  STAR_RECENT_DAYS: 900    # Look-back window for goalscorer data

HEAD-TO-HEAD:
  H2H_MATCHES: 8           # Number of recent meetings to analyze
  H2H_WEIGHT: 0.05         # Maximum lambda adjustment from H2H

SIMULATION:
  MAX_GOALS: 8             # Maximum goals per team in score matrix
  N_SIMULATIONS: 10200     # Monte Carlo simulation count

### Tuning Tips
- If predictions are too draw-heavy: increase DIXON_COLES_RHO magnitude
- If top teams are too close: increase MAX_RATIO
- If rankings dominate too much: decrease RANK_WEIGHT values
- If recent form matters more: increase DECAY_RATE
- If star players dominate: reduce cap in get_team_star_impact

---

## Data Sources

### Historical Match Results (results.csv)
- Source: Kaggle International Football Results dataset
- Coverage: 1872 to January 2026
- 49,000+ matches
- Fields: date, home_team, away_team, home_score, away_score, tournament, city, country, neutral

### FIFA Rankings (rankings.csv)
- Source: FIFA official rankings
- Fields: rank, country_full, total_points, previous_points, rank_change

### Goalscorer Records (goalscorers.csv)
- Source: Kaggle International Football Goalscorers dataset
- 47,000+ individual goal records
- Fields: date, home_team, away_team, team, scorer, minute, own_goal, penalty

---

## Known Limitations

1. DATA FRESHNESS: Base dataset ends January 2026. Use recent_results.csv for newer matches.

2. STAR PLAYER DETECTION: Only based on international goals. Club form not considered.
   Players who score lots for clubs but not nationally wont be boosted.

3. CARD PREDICTION: Basic model using defensive stats and intensity.
   No historical card data used. Treat as rough estimate only.

4. GOALKEEPER QUALITY: Not modeled. Teams with elite keepers dont get defensive boost.

5. INJURIES/SUSPENSIONS: Not tracked. Star player boosts assume all players available.

6. TACTICAL MATCHUPS: Model doesnt consider tactical styles or formations.

7. 1-1 STILL APPEARS HIGH: Dixon-Coles rho=-0.08 helps but 1-1 can still be top-2 in close matches.

8. TEAM NAME MATCHING: Names must exactly match database. No fuzzy matching for team inputs.

---

## Troubleshooting

PROBLEM: Prediction doesnt change after adding recent result
SOLUTION: Cache may be stale. Restart the Streamlit app or call clear_cache() in CLI.

PROBLEM: Team not found
SOLUTION: Check exact spelling. Run: python -c "from prediction_engine import get_all_teams; print(get_all_teams())"

PROBLEM: ImportError for clear_cache
SOLUTION: Run fix_cache.py or manually add the function to prediction_engine.py

PROBLEM: Charts not generating
SOLUTION: Ensure charts/ directory exists. Run: mkdir charts

PROBLEM: Streamlit Cloud deploy fails
SOLUTION: Check requirements.txt has all dependencies. Ensure no local file paths.

PROBLEM: use_container_width deprecation warning
SOLUTION: Replace use_container_width=True with width="stretch" in app.py

---

## Version History

v6.2 (Current - March 2026)
  - Admin panel in Streamlit sidebar
  - CLI match manager tool
  - Card predictor (yellow/red)
  - Recent results auto-merge system
  - clear_cache() function

v6.1 (March 2026)
  - Auto-derived star players from goalscorers.csv
  - Fuzzy name deduplication (accent + Jr/Junior)
  - Head-to-head historical analysis
  - Dixon-Coles rho: -0.04 to -0.08
  - Rank weight top: 0.40 to 0.30
  - Diminishing returns on star stacking
  - Defender filtering (min gpm 0.20)

v6.0 (March 2026)
  - Dixon-Coles Poisson model
  - Monte Carlo simulation (10,200)
  - Manual star players (25+ teams)
  - Tournament weighting system
  - Time decay on form
  - Opponent strength adjustment
  - Bayesian shrinkage

v5.0 and earlier
  - Basic Poisson model
  - Simple ranking-based predictions
  - No star players or H2H

---

## Quick Reference Commands

Start web app:
  streamlit run app.py

Start CLI manager:
  python match_manager.py

Quick prediction (one-off):
  python test_v61.py

Check data freshness:
  python check_data_freshness.py

Diagnose specific matchup:
  python diagnose_swe_pol.py (edit teams inside)

Compile check all files:
  python -m py_compile prediction_engine.py
  python -m py_compile app.py
  python -m py_compile chart_generator.py
  python -m py_compile match_manager.py

Git deploy:
  git add -A
  git commit -m "description"
  git push origin main

---

## Contact & Credits

Built with: Python, Streamlit, Pandas, NumPy, SciPy, Matplotlib
Model: Dixon-Coles (1997) adjusted Poisson with Monte Carlo simulation
Data: Kaggle International Football datasets
UI: Retro 2000s neon dark theme

---
# END OF DOCUMENTATION
