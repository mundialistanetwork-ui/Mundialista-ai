# Mundialista AI - v6 System Documentation
# Complete Technical Reference
# Last Updated: March 2026

---

# 1. Update Overview

## Version History

| Version | Key Changes |
|---------|-------------|
| v1-v3   | Separate CLI and Streamlit engines |
| v4      | Unified prediction_engine.py |
| v5      | Premium green/gold/ivory visual redesign |
| v5.1    | Charts always generated, Streamlit tabs |
| v6      | Major engine upgrade (current) |

## What is Mundialista AI?

A Python-based international football match prediction system that:
- Predicts match outcomes using attack/defense Poisson modeling
- Uses Dixon-Coles low-score correction
- Computes exact probabilities via Poisson score matrix
- Applies time-weighted form with exponential decay
- Adjusts for opponent strength and tournament importance
- Uses real FIFA rankings (201 teams) + historical data (4,200+ matches)
- Tracks star players for 21 nations
- Generates 5 chart types + HTML reports
- Has CLI and Streamlit interfaces sharing one engine

## What changed in v6?

The prediction engine was completely rebuilt.

| Feature                    | v5 (old)                        | v6 (new)                              |
|----------------------------|---------------------------------|---------------------------------------|
| Team modeling              | Single lambda per team          | Separate attack + defense ratings     |
| Lambda calculation         | (goals_for + goals_against) / 2 | attack_A x defense_B x league_avg    |
| Low-score correction       | None                            | Dixon-Coles rho parameter             |
| Probability calculation    | Monte Carlo 10,200 sims         | Exact Poisson score matrix            |
| Form weighting             | All matches equal               | Exponential time decay                |
| Opponent adjustment        | None                            | Opponent strength factor              |
| Tournament weighting       | None                            | World Cup > qualifier > friendly      |
| Form window                | 12 matches                      | 20 matches                            |
| Compression mechanisms     | 5 steps (regression, convergence, draw boost) | Removed - model is smarter |
| Data caching               | None                            | Global cache for CSVs                 |
| 1-1 dominance              | Every close match               | Fixed - varied scorelines             |
| Speed                      | ~2-4 seconds per prediction     | Near instant (exact math)             |

---

# 2. Engine Architecture

## Model Type

Mundialista AI v6 is a:
- Dixon-Coles adjusted independent Poisson model
- With separate attack and defense ratings
- Blending form-based and ranking-based estimates
- Using time-weighted opponent-adjusted historical data
- Computing exact probabilities via score matrix

## Pipeline Overview

Input: Two team names (e.g., Argentina, Brazil)

Step 1: LOAD DATA
    - Get last 20 matches for each team
    - Weight each match by:
      - Time decay (recent = more weight)
      - Tournament importance (World Cup > friendly)
      - Opponent strength (goals vs Brazil > goals vs San Marino)
    - Calculate weighted goals for and goals against

Step 2: COMPUTE ATTACK AND DEFENSE RATINGS
    - attack = weighted_goals_scored / global_average
    - defense = weighted_goals_conceded / global_average
    - attack > 1.0 = scores more than average
    - attack < 1.0 = scores less than average
    - defense > 1.0 = concedes more than average (bad)
    - defense < 1.0 = concedes less than average (good)

Step 3: SHRINKAGE
    - Pull extreme ratings toward global average
    - Prevents overfitting to small samples
    - Strength controlled by SHRINK_K = 8

Step 4: FORM-BASED LAMBDAS
    - lambda_form_A = attack_A x defense_B x global_avg
    - lambda_form_B = attack_B x defense_A x global_avg
    - This captures matchup dynamics:
      - Strong attack vs weak defense = high lambda
      - Weak attack vs strong defense = low lambda

Step 5: RANKING-BASED LAMBDAS
    - Log curve from FIFA ranking
    - lambda_rank_A = global_avg x rank_factor_A / rank_factor_B
    - Provides baseline from official rankings

Step 6: BLEND RANKING + FORM
    - Top-30 vs Top-30: 40% ranking, 60% form
    - Other matches: 25% ranking, 75% form
    - Form gets more weight because attack/defense model is now stronger

Step 7: STAR PLAYERS
    - 21 nations have tracked star players
    - Relative system: advantage only if opponent has fewer/weaker stars
    - Capped at 20% max boost

Step 8: HOME ADVANTAGE
    - Home team: lambda x 1.06
    - Away team: lambda x 0.94
    - Neutral: no adjustment

Step 9: RATIO CAP (top-30 only)
    - Max ratio between lambdas: 1.35x
    - Wider than v5 (was 1.15) because model is more accurate

Step 10: EXACT POISSON MATRIX + DIXON-COLES
    - Generate probability for every scoreline 0-0 through 8-8
    - Apply Dixon-Coles correction to low scores
    - Sum matrix regions for win/draw/loss probabilities
    - No Monte Carlo randomness - deterministic and instant

---

# 3. How Attack/Defense Ratings Work

## The Core Idea

Every team gets two numbers:
- Attack rating: how effectively they score
- Defense rating: how much they concede

These are RELATIVE to the global average (1.36 goals per game).

## Interpretation Guide

| Attack Rating | Meaning                    | Example Teams        |
|---------------|----------------------------|----------------------|
| > 1.5         | Elite attack               | Spain, Portugal      |
| 1.2 - 1.5     | Strong attack              | Argentina, France    |
| 0.9 - 1.2     | Average attack             | Most mid-tier teams  |
| < 0.9         | Weak attack                | Bolivia, San Marino  |

| Defense Rating | Meaning                   | Example Teams        |
|----------------|---------------------------|----------------------|
| < 0.6          | Elite defense (concedes little) | Argentina       |
| 0.6 - 0.85     | Strong defense             | Portugal, France     |
| 0.85 - 1.1     | Average defense            | Most teams           |
| > 1.1          | Weak defense (concedes a lot) | Bolivia           |

## How Lambda Is Calculated From Ratings

    lambda_A = attack_A x defense_B x global_average

This means:
- A strong attack against a weak defense = HIGH lambda (lots of goals)
- A weak attack against a strong defense = LOW lambda (few goals)
- Two average teams = lambda near global average

## Example: Argentina vs Brazil

    Argentina attack: 1.33 (strong)
    Argentina defense: 0.46 (elite)
    Brazil attack: 1.13 (above average)
    Brazil defense: 0.76 (strong)

    lambda_Argentina = 1.33 x 0.76 x 1.36 = ~1.37
    lambda_Brazil = 1.13 x 0.46 x 1.36 = ~0.71

    (After blending with ranking-based estimates and adjustments)
    Final: lambda_A = 1.20, lambda_B = 0.89

This correctly captures that Argentina has the edge in both attack and defense.

## How Ratings Are Computed From Data

For each of a team's last 20 matches:
1. Get goals scored and goals conceded
2. Multiply by three weights:
   - Time weight: exp(-0.003 x days_ago)
   - Tournament weight: World Cup = 1.0, friendly = 0.5
   - Opponent strength: based on opponent FIFA ranking
3. Compute weighted average goals for and goals against
4. Apply shrinkage toward global average
5. Divide by global average to get rating

---

# 4. Dixon-Coles Low-Score Correction

## What Is It?

Standard Poisson assumes goals are independent. But in real football:
- 0-0 draws are slightly more common than Poisson predicts
- 1-1 draws are slightly less common than pure Poisson predicts
- 1-0 and 0-1 results need small adjustments

Dixon-Coles (1997) introduced a single parameter rho that corrects
the joint probability of low-scoring outcomes.

## How It Works

For each scoreline (i, j), the base probability is:
    P(i, j) = Poisson(i, lambda_A) x Poisson(j, lambda_B)

Then Dixon-Coles applies a correction ONLY for scores where both
teams score 0 or 1:

    If 0-0: multiply by (1 + rho x lambda_A x lambda_B)
    If 0-1: multiply by (1 - rho x lambda_A)
    If 1-0: multiply by (1 - rho x lambda_B)
    If 1-1: multiply by (1 + rho)
    All other scores: no change

## Current Setting

    rho = -0.04

A negative rho means:
- 0-0 probability slightly reduced
- 1-0 and 0-1 probability slightly increased
- 1-1 probability slightly reduced

This directly addresses the old 1-1 dominance problem.

## Why This Matters

Without Dixon-Coles, independent Poisson tends to overpredict
certain low-score combinations, especially 1-1. The correction
makes the score distribution more realistic.

---

# 5. Exact Poisson Matrix vs Monte Carlo

## Old Approach (v5): Monte Carlo Simulation

    - Generate 10,200 random match simulations
    - Count outcomes
    - Convert to percentages

Problems:
    - Slow (thousands of random draws)
    - Non-deterministic (different results each run)
    - Less precise (sampling noise)

## New Approach (v6): Exact Score Matrix

    - Calculate P(i, j) for every scoreline 0-0 through 8-8
    - Apply Dixon-Coles correction
    - Sum regions of matrix for exact probabilities

Benefits:
    - Near instant (no simulation loop)
    - Deterministic (same input = same output)
    - More precise (exact math, no sampling noise)
    - Still generates simulation arrays for backward compatibility

## How Win/Draw/Loss Are Computed

    Team A wins = sum of all P(i, j) where i > j
    Draw = sum of all P(i, j) where i == j
    Team B wins = sum of all P(i, j) where i < j

## Score Matrix Size

Default: 9x9 (goals 0 through 8)
This captures 99.9%+ of realistic football outcomes.

---

# 6. Time Weighting and Tournament Weighting

## Time-Weighted Form

Not all matches in a team's history matter equally.
A match from last week should count more than one from a year ago.

Formula: weight = exp(-decay_rate x days_ago)

    decay_rate = 0.003
    Match 7 days ago: weight = 0.98 (almost full weight)
    Match 30 days ago: weight = 0.91
    Match 90 days ago: weight = 0.76
    Match 180 days ago: weight = 0.58
    Match 365 days ago: weight = 0.33
    Match 730 days ago: weight = 0.11

This means recent form matters much more than old results.

## Tournament Importance Weighting

Different competitions carry different weight:

    FIFA World Cup: 1.0
    Copa America: 0.9
    UEFA Euro: 0.9
    Africa Cup of Nations: 0.85
    AFC Asian Cup: 0.85
    UEFA Nations League: 0.85
    FIFA World Cup qualification: 0.8
    CONCACAF Gold Cup: 0.8
    Friendly: 0.5
    Other/unknown: 0.65

This means:
- World Cup results count at full value
- Friendly results count at half value
- A World Cup goal is worth twice a friendly goal

## Opponent Strength Adjustment

Goals against strong opponents are worth more than goals against weak ones.

    opponent_strength = ranking_factor(opponent_rank) / ranking_factor(50)

This means:
- Scoring 2 against France (rank 2) gets higher weight
- Scoring 2 against a rank 150 team gets lower weight
- Benchmark is rank 50 (neutral = 1.0)

## Combined Weight Per Match

Each historical match gets a combined weight:

    match_weight = time_weight x tournament_weight x opponent_strength

Example:
- World Cup match vs Brazil, 30 days ago:
  0.91 x 1.0 x 1.15 = 1.05 (high weight)

- Friendly vs rank 120 team, 300 days ago:
  0.41 x 0.5 x 0.82 = 0.17 (low weight)

---

# 7. Complete File Reference

## Project Structure

    mundialista-ai/
    |
    |-- CORE ENGINE
    |   |-- prediction_engine.py    (v6: attack/defense + Dixon-Coles)
    |
    |-- VISUALIZATION
    |   |-- chart_generator.py      (v5: green/gold/ivory theme)
    |
    |-- INTERFACES
    |   |-- app.py                  (v5.1: premium UI + tabbed charts)
    |   |-- predict.py              (v5.1: always generates charts)
    |
    |-- DEPLOY
    |   |-- mundialista-ai/app.py   (wrapper, unchanged)
    |   |-- .streamlit/config.toml  (v5: theme config)
    |   |-- .gitignore              (v5: excludes backups/output)
    |
    |-- DATA
    |   |-- data/results.csv        (4,200+ international matches)
    |   |-- data/rankings.csv       (201 FIFA-ranked teams)
    |   |-- data/goalscorers.csv    (47,000+ goals with scorer names)
    |   |-- data/shootouts.csv      (penalty shootout history)
    |
    |-- OUTPUT
    |   |-- predictions_output/     (generated charts and reports)
    |
    |-- DOCS
    |   |-- SYSTEM_DOCS_v6.md       (this file)

## prediction_engine.py (v6)

Functions:
    load_results()           - Load match CSV (cached)
    load_rankings()          - Load FIFA rankings CSV (cached)
    get_all_teams()          - List all teams in database
    get_team_ranking(team)   - Get FIFA rank (default 100)
    get_team_points(team)    - Get FIFA points (default 1000)
    get_team_star_impact(team) - Star player multiplier
    get_ranking_factor(rank) - Log curve for ranking
    shrink_to_global(val, n, mean) - Bayesian shrinkage
    get_tournament_weight(name) - Tournament importance
    get_time_weight(date)    - Exponential time decay
    get_opponent_strength(rank) - Opponent quality factor
    get_team_stats(team)     - Full team stats with attack/defense
    dixon_coles_adjust(...)  - Low-score probability correction
    get_score_matrix(la, lb) - Exact Poisson probability matrix
    predict(team_a, team_b)  - Main prediction function

## chart_generator.py (v5)

Functions:
    generate_summary_chart(result, team_a, team_b)
    generate_probability_chart(result, team_a, team_b)
    generate_score_matrix_chart(result, team_a, team_b)
    generate_top_scores_chart(result, team_a, team_b)
    generate_goal_distribution_chart(result, team_a, team_b)
    generate_html_report(result, team_a, team_b, chart_paths)
    generate_all_charts(result, team_a, team_b)

## app.py (v5.1)

Features:
    - Green/gold/ivory premium UI
    - Card-based layout with hero banner
    - Prediction with st.session_state persistence
    - 5 tabbed chart views
    - HTML report download button
    - Loading spinner
    - Cached team list and predictions

## predict.py (v5.1)

Features:
    - Charts always generate on every prediction
    - --open flag to open HTML in browser
    - Interactive mode
    - Clean aligned output

---

# 8. Configuration Reference

    CONFIG = {
        GLOBAL_GF: 1.36              Global average goals scored
        GLOBAL_GA: 1.36              Global average goals conceded
        SHRINK_K: 8                  Shrinkage strength (lower = less shrinkage)
        LAST_N_MATCHES: 20           Form window (was 12 in v5)
        DECAY_RATE: 0.003            Time decay rate for exponential weighting
        HOME_ADVANTAGE: 1.06         Home lambda multiplier (was 1.04)
        AWAY_DISADVANTAGE: 0.94      Away lambda multiplier (was 0.96)
        RANK_WEIGHT_TOP: 0.40        Ranking weight for top-30 matches (was 0.55)
        RANK_WEIGHT_OTHER: 0.25      Ranking weight for other matches (was 0.35)
        TOP_TEAM_THRESHOLD: 30       Definition of top team
        MAX_RATIO: 1.35              Lambda ratio cap (was 1.15)
        DIXON_COLES_RHO: -0.04       Low-score correction parameter
        MAX_GOALS: 8                 Score matrix size
        N_SIMULATIONS: 10200         Simulation count (for backward compat)
        TOURNAMENT_WEIGHTS: {...}    Tournament importance weights
        DEFAULT_TOURNAMENT_WEIGHT: 0.65  Fallback tournament weight
    }

Changes from v5:
    - SHRINK_K: 10 -> 8 (less shrinkage, trust data more)
    - LAST_N_MATCHES: 12 -> 20 (wider form window)
    - HOME_ADVANTAGE: 1.04 -> 1.06 (slightly stronger)
    - AWAY_DISADVANTAGE: 0.96 -> 0.94 (slightly stronger)
    - RANK_WEIGHT_TOP: 0.55 -> 0.40 (form matters more now)
    - RANK_WEIGHT_OTHER: 0.35 -> 0.25 (form matters more now)
    - MAX_RATIO: 1.15 -> 1.35 (allow more separation)
    - NEW: DECAY_RATE, DIXON_COLES_RHO, MAX_GOALS, TOURNAMENT_WEIGHTS
    - REMOVED: FORM_REGRESSION_TOP/OTHER, CONVERGENCE_RANGE/PULL, DRAW_RANGE/TARGET/PULL

---

# 9. Return Dictionary Reference

    predict(team_a, team_b, home=None) returns:

    {
        "team_a": str,              Team A name
        "team_b": str,              Team B name
        "team_a_win": float,        Win probability percentage
        "draw": float,              Draw probability percentage
        "team_b_win": float,        Win probability percentage
        "team_a_lambda": float,     Expected goals team A
        "team_b_lambda": float,     Expected goals team B
        "team_a_rank": int,         FIFA ranking
        "team_b_rank": int,         FIFA ranking
        "team_a_points": int,       FIFA points
        "team_b_points": int,       FIFA points
        "team_a_stars": list,       Star player names
        "team_b_stars": list,       Star player names
        "team_a_star_boost": float, Star multiplier
        "team_b_star_boost": float, Star multiplier
        "team_a_attack": float,     NEW: Attack rating
        "team_a_defense": float,    NEW: Defense rating
        "team_b_attack": float,     NEW: Attack rating
        "team_b_defense": float,    NEW: Defense rating
        "match_type": str,          Elite Clash / Competitive / etc
        "rank_gap": int,            Absolute rank difference
        "home": str or None,        Home team or None
        "top_scores": list,         Top 10 scorelines with counts
        "goals_a": ndarray,         Simulated goals (backward compat)
        "goals_b": ndarray,         Simulated goals (backward compat)
        "n_simulations": int,       Simulation count
    }

New fields in v6:
    - team_a_attack, team_a_defense
    - team_b_attack, team_b_defense

Note: goals_a and goals_b arrays are still generated via Monte Carlo
for backward compatibility with chart_generator.py goal distribution
chart. The win/draw/loss probabilities come from the exact matrix.

---

# 10. Quick Commands

    cd C:\Users\bayen\mundialista-ai
    .\venv\Scripts\Activate.ps1

    # CLI (always generates charts):
    python predict.py Argentina Brazil
    python predict.py Argentina Brazil --open
    python predict.py                          (interactive)

    # Web:
    streamlit run app.py

    # Engine test:
    python prediction_engine.py

    # Direct prediction:
    python -c "from prediction_engine import predict; r=predict('Argentina','Brazil'); print(r['team_a_win'], r['draw'], r['team_b_win'])"

    # Check attack/defense:
    python -c "from prediction_engine import get_team_stats; s=get_team_stats('Argentina'); print('Attack:', s['attack'], 'Defense:', s['defense'])"

    # Chart generation:
    python -c "from prediction_engine import predict; from chart_generator import generate_all_charts; r=predict('Argentina','Brazil'); print(generate_all_charts(r,'Argentina','Brazil'))"

    # Syntax checks:
    python -m py_compile prediction_engine.py
    python -m py_compile chart_generator.py
    python -m py_compile predict.py
    python -m py_compile app.py

---

# 11. Known Issues and Notes

## PowerShell encoding
All .py files must be saved as UTF-8:
    Set-Content filename.py -Encoding utf8

Avoid in PowerShell heredocs:
    - Dollar signs (variable interpolation)
    - Middle dots, em/en dashes, smart quotes
    - Use string concatenation not f-strings

## Defense rating interpretation
    - LOWER defense = BETTER (concedes less)
    - HIGHER defense = WORSE (concedes more)
    - This is counterintuitive but mathematically correct
    - defense = goals_conceded / global_average

## Backward compatibility
    - goals_a and goals_b arrays still generated via Monte Carlo
    - These are used by chart_generator.py for goal distribution
    - Win/draw/loss percentages come from exact matrix (more accurate)
    - top_scores come from exact matrix (deterministic)

## Star player system
    - Still manual (21 nations hardcoded)
    - Future upgrade: derive from goalscorers.csv automatically

## Streamlit caching
    - Team list cached via st.cache_data
    - If data files update, clear cache or restart

## Data caching in engine
    - results.csv and rankings.csv cached in memory after first load
    - If files change during a session, restart Python to reload

---

# 12. Sample Predictions (v6 engine)

## Elite Clash: Argentina vs Brazil
    Result: 43.8% | 28.4% | 27.8%
    Lambdas: 1.20 vs 0.89
    Attack/Defense A: 1.331 / 0.456
    Attack/Defense B: 1.128 / 0.759
    Top: 1-0, 1-1, 0-0, 0-1, 2-0

## Elite Clash: Spain vs Germany
    Result: 44.2% | 22.2% | 33.6%
    Attack/Defense A: 1.991 / 0.755
    Attack/Defense B: 1.597 / 0.720
    Top: 1-1, 2-1, 1-2, 1-0, 2-2

## Competitive: Italy vs France
    Result: 28.9% | 22.1% | 48.9%
    Attack/Defense A: 1.526 / 1.100
    Attack/Defense B: 1.574 / 0.742
    Top: 1-1, 1-2, 0-1, 0-2, 2-1

## Total Mismatch: France vs San Marino
    Result: 97.1% | 2.1% | 0.7%
    Lambdas: 5.153 vs 0.504
    Top: 5-0, 4-0, 6-0, 3-0, 7-0

---

# 13. Emergency Rollback

## Restore v5 engine from backup:
    Copy-Item prediction_engine_v5_backup.py prediction_engine.py
    python -m py_compile prediction_engine.py
    git add prediction_engine.py
    git commit -m "Rollback engine to v5"
    git push

## Revert last commit:
    git revert HEAD
    git push

## Check backups:
    Get-ChildItem *backup* | Select-Object Name, LastWriteTime

---

# 14. Future Upgrade Roadmap

## Phase 1: Already Done (v6)
    - Separate attack/defense ratings
    - Dixon-Coles correction
    - Exact Poisson matrix
    - Time-weighted form
    - Opponent strength adjustment
    - Tournament weighting

## Phase 2: Next Upgrades
    - Confederation strength adjustment
    - Head-to-head history factor
    - Auto-derived star player boosts from goalscorers.csv
    - Momentum/streak detection
    - Full tournament simulation (World Cup bracket)

## Phase 3: Advanced
    - Goal timing model (from goalscorers.csv minute data)
    - Upset probability model
    - Betting value finder
    - Auto-updating data pipeline

---

# Final Checklist

    python -m py_compile prediction_engine.py
    python -m py_compile chart_generator.py
    python -m py_compile predict.py
    python -m py_compile app.py
    python prediction_engine.py
    python predict.py Argentina Brazil
    python predict.py France England
    python predict.py Brazil Bolivia
    streamlit run app.py
    git status
    git log --oneline -5
    git push
