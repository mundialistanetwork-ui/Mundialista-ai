# prediction_engine.py - THE ONE SOURCE OF TRUTH
"""
Unified prediction engine for Mundialista-AI.
Used by both CLI (predict.py) and Web (app.py).
"""

import numpy as np
from scipy.stats import poisson
import pandas as pd
import os

# ============== CONFIGURATION ==============
CONFIG = {
    # Global baselines
    "GLOBAL_GF": 1.36,
    "GLOBAL_GA": 1.36,
    
    # Shrinkage
    "SHRINK_K": 10,
    "LAST_N_MATCHES": 12,
    
    # Home advantage
    "HOME_ADVANTAGE": 1.04,
    "AWAY_DISADVANTAGE": 0.96,
    
    # Ranking weights
    "RANK_WEIGHT_TOP": 0.55,
    "RANK_WEIGHT_OTHER": 0.35,
    
    # Form regression
    "FORM_REGRESSION_TOP": 0.50,
    "FORM_REGRESSION_OTHER": 0.30,
    
    # Convergence
    "CONVERGENCE_RANGE": 50,
    "CONVERGENCE_PULL": 0.40,
    
    # Draw boost
    "DRAW_RANGE": 35,
    "DRAW_TARGET": 1.15,
    "DRAW_PULL": 0.20,
    
    # Caps
    "MAX_RATIO": 1.15,
    "TOP_TEAM_THRESHOLD": 30,
    
    # Simulation
    "N_SIMULATIONS": 10200,
}


# ============== DATA LOADING ==============

def load_results():
    """Load match results from CSV"""
    try:
        df = pd.read_csv("data/results.csv")
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    except FileNotFoundError:
        print("ERROR: data/results.csv not found")
        return pd.DataFrame()


def load_rankings():
    """Load FIFA rankings from CSV"""
    try:
        return pd.read_csv("data/rankings.csv")
    except FileNotFoundError:
        print("WARNING: data/rankings.csv not found, using defaults")
        return pd.DataFrame()


def get_all_teams():
    """Get list of all teams in the database"""
    df = load_results()
    if df.empty:
        return []
    teams = sorted(set(df['home_team'].unique()) | set(df['away_team'].unique()))
    return teams


def get_team_ranking(team: str) -> int:
    """Get FIFA rank for a team (default 100 if not found)"""
    rankings = load_rankings()
    if rankings.empty:
        return 100
    
    match = rankings[rankings['country_full'].str.lower() == team.lower()]
    if len(match) > 0:
        return int(match.iloc[0]['rank'])
    return 100


def get_team_points(team: str) -> int:
    """Get FIFA points for a team"""
    rankings = load_rankings()
    if rankings.empty:
        return 1500
    
    match = rankings[rankings['country_full'].str.lower() == team.lower()]
    if len(match) > 0:
        return int(match.iloc[0]['total_points'])
    return 1500


# ============== STAR PLAYERS ==============

STAR_PLAYERS = {
    "Argentina": {
        "Lionel Messi": {"attack": 1.15, "status": "active"},
        "Lautaro Martinez": {"attack": 1.08, "status": "active"},
        "Julian Alvarez": {"attack": 1.06, "status": "active"},
    },
    "France": {
        "Kylian Mbappe": {"attack": 1.15, "status": "active"},
        "Antoine Griezmann": {"attack": 1.06, "status": "active"},
    },
    "Brazil": {
        "Vinicius Jr": {"attack": 1.12, "status": "active"},
        "Raphinha": {"attack": 1.06, "status": "active"},
        "Rodrygo": {"attack": 1.05, "status": "active"},
    },
    "England": {
        "Harry Kane": {"attack": 1.12, "status": "active"},
        "Bukayo Saka": {"attack": 1.08, "status": "active"},
        "Jude Bellingham": {"attack": 1.10, "status": "active"},
    },
    "Spain": {
        "Lamine Yamal": {"attack": 1.10, "status": "active"},
        "Alvaro Morata": {"attack": 1.06, "status": "active"},
        "Dani Olmo": {"attack": 1.06, "status": "active"},
    },
    "Germany": {
        "Florian Wirtz": {"attack": 1.10, "status": "active"},
        "Jamal Musiala": {"attack": 1.10, "status": "active"},
        "Kai Havertz": {"attack": 1.06, "status": "active"},
    },
    "Portugal": {
        "Cristiano Ronaldo": {"attack": 1.10, "status": "active"},
        "Bruno Fernandes": {"attack": 1.08, "status": "active"},
        "Bernardo Silva": {"attack": 1.06, "status": "active"},
    },
    "Norway": {
        "Erling Haaland": {"attack": 1.18, "status": "active"},
        "Martin Odegaard": {"attack": 1.08, "status": "active"},
    },
    "Egypt": {
        "Mohamed Salah": {"attack": 1.12, "status": "active"},
    },
    "South Korea": {
        "Son Heung-min": {"attack": 1.12, "status": "active"},
    },
    "Belgium": {
        "Romelu Lukaku": {"attack": 1.10, "status": "active"},
        "Kevin De Bruyne": {"attack": 1.10, "status": "active"},
    },
    "Netherlands": {
        "Cody Gakpo": {"attack": 1.08, "status": "active"},
        "Memphis Depay": {"attack": 1.06, "status": "active"},
    },
    "Colombia": {
        "Luis Diaz": {"attack": 1.08, "status": "active"},
        "James Rodriguez": {"attack": 1.06, "status": "active"},
    },
    "Uruguay": {
        "Darwin Nunez": {"attack": 1.08, "status": "active"},
        "Federico Valverde": {"attack": 1.06, "status": "active"},
    },
    "Croatia": {
        "Luka Modric": {"attack": 1.06, "status": "active"},
    },
    "Japan": {
        "Takefusa Kubo": {"attack": 1.06, "status": "active"},
        "Kaoru Mitoma": {"attack": 1.06, "status": "active"},
    },
    "United States": {
        "Christian Pulisic": {"attack": 1.08, "status": "active"},
        "Weston McKennie": {"attack": 1.04, "status": "active"},
    },
    "Mexico": {
        "Raul Jimenez": {"attack": 1.06, "status": "active"},
    },
    "Senegal": {
        "Sadio Mane": {"attack": 1.10, "status": "active"},
    },
    "Morocco": {
        "Hakim Ziyech": {"attack": 1.07, "status": "active"},
        "Achraf Hakimi": {"attack": 1.05, "status": "active"},
    },
    "Italy": {
        "Federico Chiesa": {"attack": 1.06, "status": "active"},
    },
}


def get_team_star_impact(team: str) -> dict:
    """Get combined star player impact for a team"""
    if team not in STAR_PLAYERS:
        return {"attack": 1.0, "players": []}
    
    players = STAR_PLAYERS[team]
    active_players = {k: v for k, v in players.items() if v.get("status") == "active"}
    
    if not active_players:
        return {"attack": 1.0, "players": []}
    
    # Combine boosts (diminishing returns)
    total_boost = 1.0
    for name, data in active_players.items():
        individual_boost = data.get("attack", 1.0) - 1.0
        total_boost += individual_boost * 0.7  # Diminishing returns
    
    # Cap at 20%
    total_boost = min(total_boost, 1.20)
    
    return {
        "attack": total_boost,
        "players": list(active_players.keys())
    }


# ============== CORE FUNCTIONS ==============

def get_team_stats(team: str) -> dict:
    """Get team's recent form from last N matches"""
    df = load_results()
    last_n = CONFIG["LAST_N_MATCHES"]
    
    if df.empty:
        return {
            "avg_gf": CONFIG["GLOBAL_GF"],
            "avg_ga": CONFIG["GLOBAL_GA"],
            "home_gf": CONFIG["GLOBAL_GF"],
            "away_gf": CONFIG["GLOBAL_GF"],
            "matches": 0,
        }
    
    # Get matches where team played
    home_matches = df[df['home_team'] == team].tail(last_n)
    away_matches = df[df['away_team'] == team].tail(last_n)
    
    # Calculate averages
    if len(home_matches) > 0:
        home_gf = home_matches['home_score'].mean()
        home_ga = home_matches['away_score'].mean()
    else:
        home_gf = CONFIG["GLOBAL_GF"]
        home_ga = CONFIG["GLOBAL_GA"]
    
    if len(away_matches) > 0:
        away_gf = away_matches['away_score'].mean()
        away_ga = away_matches['home_score'].mean()
    else:
        away_gf = CONFIG["GLOBAL_GF"]
        away_ga = CONFIG["GLOBAL_GA"]
    
    matches_found = len(home_matches) + len(away_matches)
    
    return {
        "avg_gf": (home_gf + away_gf) / 2,
        "avg_ga": (home_ga + away_ga) / 2,
        "home_gf": home_gf,
        "away_gf": away_gf,
        "matches": matches_found,
    }


def shrink_to_global(value: float, n_matches: int, global_mean: float) -> float:
    """Bayesian shrinkage toward global average"""
    k = CONFIG["SHRINK_K"]
    return (value * n_matches + global_mean * k) / (n_matches + k)


def get_ranking_factor(rank: int) -> float:
    """Log curve for ranking impact"""
    log_factor = 0.10
    return 1 + log_factor * np.log(201 / max(rank, 1))


# ============== MAIN PREDICTION ==============

def predict(team_a: str, team_b: str, home: str = None) -> dict:
    """
    Main prediction function.
    
    Args:
        team_a: First team name
        team_b: Second team name
        home: Home team (None for neutral)
    
    Returns:
        Complete prediction result dictionary
    """
    
    # ===== 1. GET RAW STATS =====
    stats_a = get_team_stats(team_a)
    stats_b = get_team_stats(team_b)
    
    # ===== 2. SHRINKAGE =====
    gf_a = shrink_to_global(stats_a["avg_gf"], stats_a["matches"], CONFIG["GLOBAL_GF"])
    ga_a = shrink_to_global(stats_a["avg_ga"], stats_a["matches"], CONFIG["GLOBAL_GA"])
    gf_b = shrink_to_global(stats_b["avg_gf"], stats_b["matches"], CONFIG["GLOBAL_GF"])
    ga_b = shrink_to_global(stats_b["avg_ga"], stats_b["matches"], CONFIG["GLOBAL_GA"])
    
    # ===== 3. FIFA RANKINGS =====
    rank_a = get_team_ranking(team_a)
    rank_b = get_team_ranking(team_b)
    points_a = get_team_points(team_a)
    points_b = get_team_points(team_b)
    
    rank_factor_a = get_ranking_factor(rank_a)
    rank_factor_b = get_ranking_factor(rank_b)
    
    # Ranking-implied lambda
    lambda_rank_a = CONFIG["GLOBAL_GF"] * rank_factor_a / rank_factor_b
    lambda_rank_b = CONFIG["GLOBAL_GF"] * rank_factor_b / rank_factor_a
    
    # Form-based lambda
    lambda_form_a = (gf_a + ga_b) / 2
    lambda_form_b = (gf_b + ga_a) / 2
    
    # ===== 4. BLEND RANKING + FORM =====
    both_top = rank_a <= CONFIG["TOP_TEAM_THRESHOLD"] and rank_b <= CONFIG["TOP_TEAM_THRESHOLD"]
    
    if both_top:
        rank_weight = CONFIG["RANK_WEIGHT_TOP"]
    else:
        rank_weight = CONFIG["RANK_WEIGHT_OTHER"]
    
    form_weight = 1 - rank_weight
    
    lambda_a = rank_weight * lambda_rank_a + form_weight * lambda_form_a
    lambda_b = rank_weight * lambda_rank_b + form_weight * lambda_form_b
    
    # ===== 5. FORM REGRESSION =====
    regression = CONFIG["FORM_REGRESSION_TOP"] if both_top else CONFIG["FORM_REGRESSION_OTHER"]
    avg_lambda = (lambda_a + lambda_b) / 2
    
    lambda_a = lambda_a * (1 - regression) + avg_lambda * regression
    lambda_b = lambda_b * (1 - regression) + avg_lambda * regression
    
    # ===== 6. CONVERGENCE =====
    rank_gap = abs(rank_a - rank_b)
    
    if rank_gap < CONFIG["CONVERGENCE_RANGE"] and both_top:
        convergence = CONFIG["CONVERGENCE_PULL"]
        mid = (lambda_a + lambda_b) / 2
        lambda_a = lambda_a * (1 - convergence) + mid * convergence
        lambda_b = lambda_b * (1 - convergence) + mid * convergence
    
    # ===== 7. DRAW BOOST =====
    if rank_gap < CONFIG["DRAW_RANGE"]:
        draw_pull = CONFIG["DRAW_PULL"]
        draw_target = CONFIG["DRAW_TARGET"]
        lambda_a = lambda_a * (1 - draw_pull) + draw_target * draw_pull
        lambda_b = lambda_b * (1 - draw_pull) + draw_target * draw_pull
    
    # ===== 8. STAR PLAYERS =====
    star_data_a = get_team_star_impact(team_a)
    star_data_b = get_team_star_impact(team_b)
    star_a = star_data_a["attack"]
    star_b = star_data_b["attack"]
    
    # Relative star power
    avg_star = (star_a + star_b) / 2
    relative_star_a = star_a / avg_star if avg_star > 0 else 1.0
    relative_star_b = star_b / avg_star if avg_star > 0 else 1.0
    
    lambda_a *= relative_star_a
    lambda_b *= relative_star_b
    
    # ===== 9. HOME ADVANTAGE =====
    is_home_a = home == team_a
    is_home_b = home == team_b
    
    if is_home_a:
        lambda_a *= CONFIG["HOME_ADVANTAGE"]
        lambda_b *= CONFIG["AWAY_DISADVANTAGE"]
    elif is_home_b:
        lambda_b *= CONFIG["HOME_ADVANTAGE"]
        lambda_a *= CONFIG["AWAY_DISADVANTAGE"]
    
    # ===== 10. RATIO CAP =====
    if both_top:
        ratio = lambda_a / lambda_b if lambda_b > 0 else 1.0
        if ratio > CONFIG["MAX_RATIO"]:
            lambda_a = lambda_b * CONFIG["MAX_RATIO"]
        elif ratio < 1 / CONFIG["MAX_RATIO"]:
            lambda_b = lambda_a * CONFIG["MAX_RATIO"]
    
    # ===== 11. POISSON SIMULATION =====
    n_sims = CONFIG["N_SIMULATIONS"]
    
    goals_a = np.random.poisson(lambda_a, n_sims)
    goals_b = np.random.poisson(lambda_b, n_sims)
    
    wins_a = np.sum(goals_a > goals_b)
    draws = np.sum(goals_a == goals_b)
    wins_b = np.sum(goals_a < goals_b)
    
    # ===== 12. SCORE DISTRIBUTION =====
    score_counts = {}
    for ga, gb in zip(goals_a, goals_b):
        score = f"{ga}-{gb}"
        score_counts[score] = score_counts.get(score, 0) + 1
    
    top_scores = sorted(score_counts.items(), key=lambda x: -x[1])[:10]
    
    # ===== 13. MATCH TYPE =====
    if both_top and rank_gap < 20:
        match_type = "Elite Clash"
    elif rank_gap > 100:
        match_type = "Total Mismatch"
    elif rank_gap > 50:
        match_type = "Clear Favorite"
    else:
        match_type = "Competitive Match"
    
    return {
        # Teams
        "team_a": team_a,
        "team_b": team_b,
        
        # Probabilities
        "team_a_win": round(100 * wins_a / n_sims, 1),
        "draw": round(100 * draws / n_sims, 1),
        "team_b_win": round(100 * wins_b / n_sims, 1),
        
        # Lambdas
        "team_a_lambda": round(lambda_a, 3),
        "team_b_lambda": round(lambda_b, 3),
        
        # Rankings
        "team_a_rank": rank_a,
        "team_b_rank": rank_b,
        "team_a_points": points_a,
        "team_b_points": points_b,
        
        # Stars
        "team_a_stars": star_data_a["players"],
        "team_b_stars": star_data_b["players"],
        "team_a_star_boost": star_a,
        "team_b_star_boost": star_b,
        
        # Match info
        "match_type": match_type,
        "rank_gap": rank_gap,
        "home": home,
        
        # Scores
        "top_scores": top_scores,
        "goals_a": goals_a,
        "goals_b": goals_b,
        
        # Config
        "n_simulations": n_sims,
    }


def get_score_matrix(lambda_a: float, lambda_b: float, max_goals: int = 6) -> np.ndarray:
    """Generate probability matrix for scorelines"""
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            matrix[i, j] = poisson.pmf(i, lambda_a) * poisson.pmf(j, lambda_b)
    
    return matrix


# ============== CLI TEST ==============

if __name__ == "__main__":
    print("Testing prediction engine...")
    result = predict("Argentina", "Brazil")
    print(f"\n{result['team_a']} vs {result['team_b']}")
    print(f"Ranks: #{result['team_a_rank']} vs #{result['team_b_rank']}")
    print(f"Result: {result['team_a_win']}% | {result['draw']}% | {result['team_b_win']}%")
    print(f"Match Type: {result['match_type']}")
    print("\nEngine working correctly!")
