import pandas as pd
import os
import sys

# Import the Simulation Brain
from content_automation import quick_simulate, RESULTS_DF, ALL_TEAMS
# Import Data Layer
from data_loader import load_rankings, get_team_ranking, get_team_stats
# Import Star Power
from player_impact import get_team_star_impact

# --- Load Rankings (for App Dropdown) ---
def load_rankings_data():
    """Wrapper for app.py compatibility"""
    return load_rankings()

# --- Head-to-Head Logic ---
def get_h2h(team_a, team_b, limit=12):
    """Calculates Head-to-Head history from results.csv"""
    if RESULTS_DF is None:
        return {"h2h_matches": 0}

    # Filter matches where both teams played each other
    mask = (
        ((RESULTS_DF['home_team'] == team_a) & (RESULTS_DF['away_team'] == team_b)) |
        ((RESULTS_DF['home_team'] == team_b) & (RESULTS_DF['away_team'] == team_a))
    )
    matches = RESULTS_DF[mask].tail(limit)

    wins_a = 0
    wins_b = 0
    draws = 0

    for _, row in matches.iterrows():
        if row['home_team'] == team_a:
            if row['home_score'] > row['away_score']: wins_a += 1
            elif row['home_score'] < row['away_score']: wins_b += 1
            else: draws += 1
        else: # team_b is home
            if row['away_score'] > row['home_score']: wins_a += 1
            elif row['away_score'] < row['home_score']: wins_b += 1
            else: draws += 1

    return {
        "h2h_matches": len(matches),
        "h2h_wins_a": wins_a,
        "h2h_wins_b": wins_b,
        "h2h_draws": draws
    }

# --- Match Type Classification ---
def classify_match(rank_a, rank_b, lambda_a, lambda_b):
    """Classifies match type for UI badges"""
    gap = abs(rank_a - rank_b)
    total_xg = lambda_a + lambda_b

    if rank_a <= 10 and rank_b <= 10:
        return "Elite Clash"
    if gap > 80:
        return "Total Mismatch"
    if gap > 40:
        return "Clear Favorite"
    return "Competitive Match"

# --- Main Prediction Function ---
def predict(team_a, team_b, neutral=True):
    """
    Main entry point for app.py.
    Runs Monte Carlo simulation and formats results for the UI.
    """

    # 1. Run Monte Carlo Simulation (from content_automation)
    # Note: content_automation uses 'home' and 'away'.
    # We treat team_a as home. If neutral, content_automation handles logic
    # (currently it applies home advantage, we might need to adjust later,
    # but for now we rely on its defaults).

    sim_result = quick_simulate(team_a, team_b)

    # 2. Get Rankings
    rank_a_info = get_team_ranking(team_a)
    rank_b_info = get_team_ranking(team_b)
    rank_a = rank_a_info.get('rank', 100) if isinstance(rank_a_info, dict) else 100
    rank_b = rank_b_info.get('rank', 100) if isinstance(rank_b_info, dict) else 100

    # 3. Get Star Players
    # quick_simulate calculates impact internally, but app.py wants the names for the UI.
    boost_a = get_team_star_impact(team_a)
    boost_b = get_team_star_impact(team_b)

    # 4. Get H2H
    h2h = get_h2h(team_a, team_b)

    # 5. Classify Match
    match_type = classify_match(rank_a, rank_b, sim_result['home_lambda'], sim_result['away_lambda'])

    # 6. Format Result for app.py
    # app.py expects 'team_a_win', 'team_a_lambda', etc.

    formatted_result = {
        # Probabilities
        "team_a_win": sim_result['home_win_pct'],
        "draw": sim_result['draw_pct'],
        "team_b_win": sim_result['away_win_pct'],

        # Expected Goals (Lambda)
        "team_a_lambda": sim_result['home_exp'],
        "team_b_lambda": sim_result['away_exp'],

        # Rankings
        "team_a_rank": rank_a,
        "team_b_rank": rank_b,

        # Metadata
        "match_type": match_type,
        "top_scores": sim_result['top5_scorelines'],

        # Stars (app.py expects lists, currently returning empty list if no names available)
        "team_a_stars": [],
        "team_b_stars": [],
        "team_a_star_boost": boost_a,
        "team_b_star_boost": boost_b,

        # H2H
        "h2h_matches": h2h['h2h_matches'],
        "h2h_wins_a": h2h['h2h_wins_a'],
        "h2h_wins_b": h2h['h2h_wins_b'],
        "h2h_draws": h2h['h2h_draws'],

        # Pass through raw lambda for charts
        "home_lambda": sim_result['home_lambda'],
        "away_lambda": sim_result['away_lambda']
    }

    return formatted_result
# ---------------------------------------------------------
# PATCH: Added missing get_score_matrix for chart_generator
# ---------------------------------------------------------
def get_score_matrix(home_team, away_team):
    result = predict(home_team, away_team)
    return {
        'home_win_prob': result.get('home_win_prob', 0.33),
        'draw_prob': result.get('draw_prob', 0.33),
        'away_win_prob': result.get('away_win_prob', 0.33),
        'home_score': result.get('predicted_home_goals', 1),
        'away_score': result.get('predicted_away_goals', 1)
    }
