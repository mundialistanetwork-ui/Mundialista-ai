import pandas as pd
import os
import sys
import numpy as np
from scipy.stats import poisson

# Import the Simulation Brain
from content_automation import quick_simulate, RESULTS_DF, ALL_TEAMS
# Import Data Layer
from data_loader import load_rankings, get_team_ranking, get_team_stats
# Import Star Power
from player_impact import get_team_star_impact

# --- Load Rankings (for App Dropdown) ---
def load_rankings_data():
    return load_rankings()

# --- Head-to-Head Logic ---
def get_h2h(team_a, team_b, limit=12):
    if RESULTS_DF is None:
        return {"h2h_matches": 0}
    team_a = str(team_a)
    team_b = str(team_b)
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
        else:
            if row['away_score'] > row['home_score']: wins_a += 1
            elif row['away_score'] < row['home_score']: wins_b += 1
            else: draws += 1
    return {"h2h_matches": len(matches), "h2h_wins_a": wins_a, "h2h_wins_b": wins_b, "h2h_draws": draws}

def classify_match(rank_a, rank_b, lambda_a, lambda_b):
    gap = abs(rank_a - rank_b)
    if rank_a <= 10 and rank_b <= 10: return "Elite Clash"
    if gap > 80: return "Total Mismatch"
    if gap > 40: return "Clear Favorite"
    return "Competitive Match"

def predict(team_a, team_b, neutral=True):
    team_a = str(team_a)
    team_b = str(team_b)
    sim_result = quick_simulate(team_a, team_b)
    rank_a_info = get_team_ranking(team_a)
    rank_b_info = get_team_ranking(team_b)
    rank_a = rank_a_info.get('rank', 100) if isinstance(rank_a_info, dict) else 100
    rank_b = rank_b_info.get('rank', 100) if isinstance(rank_b_info, dict) else 100
    boost_a = get_team_star_impact(team_a)
    boost_b = get_team_star_impact(team_b)
    h2h = get_h2h(team_a, team_b)
    match_type = classify_match(rank_a, rank_b, sim_result['home_lambda'], sim_result['away_lambda'])
    return {
        "team_a_win": sim_result['home_win_pct'], "draw": sim_result['draw_pct'], "team_b_win": sim_result['away_win_pct'],
        "team_a_lambda": sim_result['home_exp'], "team_b_lambda": sim_result['away_exp'],
        "team_a_rank": rank_a, "team_b_rank": rank_b,
        "match_type": match_type, "top_scores": sim_result['top5_scorelines'],
        "team_a_stars": [], "team_b_stars": [],
        "team_a_star_boost": boost_a, "team_b_star_boost": boost_b,
        "h2h_matches": h2h['h2h_matches'], "h2h_wins_a": h2h['h2h_wins_a'], "h2h_wins_b": h2h['h2h_wins_b'], "h2h_draws": h2h['h2h_draws'],
        "home_lambda": sim_result['home_lambda'], "away_lambda": sim_result['away_lambda']
    }

def get_score_matrix(home_team, away_team, **kwargs):
    home_team = str(home_team)
    away_team = str(away_team)
    max_goals = kwargs.get('max_goals', 5)
    result = predict(home_team, away_team)
    home_exp = float(result.get('team_a_lambda', 1.5))
    away_exp = float(result.get('team_b_lambda', 1.5))
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            matrix[i][j] = poisson.pmf(i, home_exp) * poisson.pmf(j, away_exp)
    return matrix
