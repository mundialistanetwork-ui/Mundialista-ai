"""
Mundialista AI - Prediction Engine v7
Dixon-Coles Poisson model with ELO blending, star impacts, and Monte Carlo simulation.
"""

import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import poisson

# ──────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────

CONFIG = {
    # Core model parameters
    "LAST_N_MATCHES": 12,
    "DECAY_RATE": 0.003,
    "SHRINK_K": 9.4,
    "MAX_GOALS": 8,
    "N_SIMULATIONS": 10_200,
    "DIXON_COLES_RHO": -0.04,

    # Home advantage
    "HOME_ATTACK_BOOST": 1.06,
    "HOME_DEFENSE_BOOST": 0.94,  # opponent scores less at your home

    # Ranking-form blend weights
    "RANK_WEIGHT_TOP": 0.40,      # top teams: trust ranking more
    "RANK_WEIGHT_OTHER": 0.25,    # others: trust form more
    "TOP_TEAM_THRESHOLD": 30,

    # Competitive balance (prevents unrealistic blowout predictions)
    "MAX_LAMBDA_RATIO_TOP": 1.35,
    "MIN_LAMBDA": 0.25,

    # Star player impact
    "STAR_IMPACT_DAMPENING": 0.65,
    "MAX_STAR_BOOST": 1.22,

    # Tournament importance weights
    "TOURNAMENT_WEIGHTS": {
        "fifa world cup": 1.0,
        "copa america": 0.90,
        "uefa euro": 0.90,
        "africa cup of nations": 0.85,
        "afc asian cup": 0.85,
        "concacaf gold cup": 0.80,
        "uefa nations league": 0.85,
        "fifa world cup qualification": 0.80,
        "friendly": 0.50,
    },
    "DEFAULT_TOURNAMENT_WEIGHT": 0.65,
}

DATA_DIR = Path("data")

# ──────────────────────────────────────────────
#  CACHED DATA LOADING
# ──────────────────────────────────────────────

class DataStore:
    """Lazy-loading cache for all data files."""

    def __init__(self):
        self._results = None
        self._rankings = None
        self._stars = None
        self._global_avg = None

    def clear_cache(self):
        """Force reload on next access."""
        self._results = None
        self._rankings = None
        self._stars = None
        self._global_avg = None

    @property
    def results(self) -> pd.DataFrame:
        if self._results is None:
            self._results = self._load_results()
        return self._results

    @property
    def rankings(self) -> pd.DataFrame:
        if self._rankings is None:
            self._rankings = self._load_rankings()
        return self._rankings

    @property
    def stars(self) -> dict:
        if self._stars is None:
            self._stars = self._load_stars()
        return self._stars

    @property
    def global_avg(self) -> dict:
        if self._global_avg is None:
            self._global_avg = self._calculate_global_average()
        return self._global_avg

    def _load_results(self) -> pd.DataFrame:
        path = DATA_DIR / "results.csv"
        if not path.exists():
            print(f"[WARN] {path} not found. Using empty DataFrame.")
            return pd.DataFrame()
        df = pd.read_csv(path)
        # Merge recent manually-added results from match_manager
        recent_path = DATA_DIR / "recent_results.csv"
        if recent_path.exists():
            recent = pd.read_csv(recent_path)
            if not recent.empty:
                df = pd.concat([df, recent], ignore_index=True)
                print(f"[INFO] Merged {len(recent)} recent results")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.sort_values("date").reset_index(drop=True)
        return df

    def _load_rankings(self) -> pd.DataFrame:
        path = DATA_DIR / "rankings.csv"
        if not path.exists():
            print(f"[WARN] {path} not found.")
            return pd.DataFrame()
        return pd.read_csv(path)

    def _load_stars(self) -> dict:
        path = DATA_DIR / "star_players.json"
        if not path.exists():
            print(f"[INFO] {path} not found. Using built-in star data.")
            return _BUILTIN_STARS
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _calculate_global_average(self) -> dict:
        """Calculate actual global goals-per-game from the dataset."""
        df = self.results
        if df.empty:
            return {"gf": 1.36, "ga": 1.36}

        # Use last 4 years of data for current average
        cutoff = datetime.now() - pd.Timedelta(days=4 * 365)
        recent = df[df["date"] >= cutoff] if "date" in df.columns else df

        if len(recent) < 100:
            recent = df  # fallback to all data

        avg_home = recent["home_score"].mean()
        avg_away = recent["away_score"].mean()

        return {
            "gf": round((avg_home + avg_away) / 2, 4),
            "ga": round((avg_home + avg_away) / 2, 4),
        }


# Singleton
_data = DataStore()


# ──────────────────────────────────────────────
#  BUILT-IN STAR PLAYERS (fallback)
# ──────────────────────────────────────────────

_BUILTIN_STARS = {
    "Argentina": {
        "Lionel Messi":       {"attack": 1.14, "defense": 1.00, "status": "active"},
        "Lautaro Martinez":   {"attack": 1.08, "defense": 1.00, "status": "active"},
        "Julian Alvarez":     {"attack": 1.06, "defense": 1.00, "status": "active"},
    },
    "France": {
        "Kylian Mbappe":      {"attack": 1.15, "defense": 1.00, "status": "active"},
        "Antoine Griezmann":  {"attack": 1.06, "defense": 1.02, "status": "active"},
        "Mike Maignan":       {"attack": 1.00, "defense": 1.06, "status": "active"},
    },
    "Brazil": {
        "Vinicius Jr":        {"attack": 1.12, "defense": 1.00, "status": "active"},
        "Raphinha":           {"attack": 1.06, "defense": 1.00, "status": "active"},
        "Rodrygo":            {"attack": 1.05, "defense": 1.00, "status": "active"},
    },
    "England": {
        "Harry Kane":         {"attack": 1.12, "defense": 1.00, "status": "active"},
        "Jude Bellingham":    {"attack": 1.10, "defense": 1.02, "status": "active"},
        "Bukayo Saka":        {"attack": 1.08, "defense": 1.00, "status": "active"},
    },
    "Spain": {
        "Lamine Yamal":       {"attack": 1.10, "defense": 1.00, "status": "active"},
        "Rodri":              {"attack": 1.04, "defense": 1.08, "status": "active"},
        "Dani Olmo":          {"attack": 1.06, "defense": 1.00, "status": "active"},
    },
    "Germany": {
        "Florian Wirtz":      {"attack": 1.10, "defense": 1.00, "status": "active"},
        "Jamal Musiala":      {"attack": 1.10, "defense": 1.00, "status": "active"},
        "Antonio Rudiger":    {"attack": 1.00, "defense": 1.06, "status": "active"},
    },
    "Portugal": {
        "Cristiano Ronaldo":  {"attack": 1.10, "defense": 1.00, "status": "active"},
        "Bruno Fernandes":    {"attack": 1.08, "defense": 1.00, "status": "active"},
        "Bernardo Silva":     {"attack": 1.06, "defense": 1.02, "status": "active"},
    },
    "Netherlands": {
        "Cody Gakpo":         {"attack": 1.08, "defense": 1.00, "status": "active"},
        "Virgil van Dijk":    {"attack": 1.00, "defense": 1.10, "status": "active"},
    },
    "Belgium": {
        "Kevin De Bruyne":    {"attack": 1.10, "defense": 1.00, "status": "active"},
        "Romelu Lukaku":      {"attack": 1.08, "defense": 1.00, "status": "active"},
    },
    "Colombia": {
        "Luis Diaz":          {"attack": 1.08, "defense": 1.00, "status": "active"},
        "James Rodriguez":    {"attack": 1.06, "defense": 1.00, "status": "active"},
    },
    "Uruguay": {
        "Darwin Nunez":       {"attack": 1.08, "defense": 1.00, "status": "active"},
        "Federico Valverde":  {"attack": 1.05, "defense": 1.04, "status": "active"},
    },
    "Croatia": {
        "Luka Modric":        {"attack": 1.06, "defense": 1.02, "status": "active"},
    },
    "Norway": {
        "Erling Haaland":     {"attack": 1.18, "defense": 1.00, "status": "active"},
        "Martin Odegaard":    {"attack": 1.08, "defense": 1.00, "status": "active"},
    },
    "Egypt": {
        "Mohamed Salah":      {"attack": 1.12, "defense": 1.00, "status": "active"},
    },
    "South Korea": {
        "Son Heung-min":      {"attack": 1.12, "defense": 1.00, "status": "active"},
    },
    "Japan": {
        "Takefusa Kubo":      {"attack": 1.06, "defense": 1.00, "status": "active"},
        "Kaoru Mitoma":       {"attack": 1.06, "defense": 1.00, "status": "active"},
    },
    "United States": {
        "Christian Pulisic":  {"attack": 1.08, "defense": 1.00, "status": "active"},
        "Weston McKennie":    {"attack": 1.04, "defense": 1.02, "status": "active"},
    },
    "Mexico": {
        "Raul Jimenez":       {"attack": 1.06, "defense": 1.00, "status": "active"},
    },
    "Senegal": {
        "Sadio Mane":         {"attack": 1.10, "defense": 1.00, "status": "active"},
    },
    "Morocco": {
        "Hakim Ziyech":       {"attack": 1.07, "defense": 1.00, "status": "active"},
        "Achraf Hakimi":      {"attack": 1.03, "defense": 1.06, "status": "active"},
    },
    "Italy": {
        "Federico Chiesa":    {"attack": 1.06, "defense": 1.00, "status": "active"},
        "Gianluigi Donnarumma": {"attack": 1.00, "defense": 1.07, "status": "active"},
    },
}


# ──────────────────────────────────────────────
#  HELPER FUNCTIONS
# ──────────────────────────────────────────────

def get_all_teams() -> list[str]:
    df = _data.results
    if df.empty:
        return []
    teams = set(df["home_team"].unique()) | set(df["away_team"].unique())
    return sorted(teams)


def get_team_ranking(team: str) -> int:
    rankings = _data.rankings
    if rankings.empty:
        return 100
    row = rankings[rankings["country_full"] == team]
    return int(row.iloc[0]["rank"]) if len(row) > 0 else 100


def get_team_points(team: str) -> int:
    rankings = _data.rankings
    if rankings.empty:
        return 1000
    row = rankings[rankings["country_full"] == team]
    return int(row.iloc[0]["total_points"]) if len(row) > 0 else 1000


def ranking_factor(rank: int) -> float:
    """Log-scaled ranking advantage. Rank 1 ≈ 1.53, Rank 50 ≈ 1.14, Rank 200 ≈ 1.0"""
    return 1.0 + 0.10 * math.log(201.0 / max(rank, 1))


def shrink_to_global(value: float, n_matches: int, global_mean: float) -> float:
    """Bayesian shrinkage — small samples pull toward global average."""
    k = CONFIG["SHRINK_K"]
    return (n_matches * value + k * global_mean) / (n_matches + k)


def tournament_weight(name) -> float:
    if not name or not isinstance(name, str):
        return CONFIG["DEFAULT_TOURNAMENT_WEIGHT"]
    name_lower = name.lower()
    for key, val in CONFIG["TOURNAMENT_WEIGHTS"].items():
        if key in name_lower:
            return val
    return CONFIG["DEFAULT_TOURNAMENT_WEIGHT"]


def time_weight(match_date) -> float:
    """Exponential decay — recent matches matter more."""
    if not isinstance(match_date, (pd.Timestamp, datetime)):
        return 0.5
    days_ago = max(0, (datetime.now() - pd.Timestamp(match_date).to_pydatetime()).days)
    return math.exp(-CONFIG["DECAY_RATE"] * days_ago)


def opponent_strength(opp_rank: int) -> float:
    """Scale weights by opponent quality. Beating rank #1 > beating rank #150."""
    return ranking_factor(opp_rank) / ranking_factor(50)


# ──────────────────────────────────────────────
#  STAR PLAYER IMPACT (attack + defense)
# ──────────────────────────────────────────────

def get_team_star_impact(team: str) -> dict:
    """
    Returns attack AND defense multipliers from active star players.
    """
    stars = _data.stars
    if team not in stars:
        return {"attack": 1.0, "defense": 1.0, "players": []}

    players = stars[team]
    active = {k: v for k, v in players.items() if v.get("status") == "active"}

    if not active:
        return {"attack": 1.0, "defense": 1.0, "players": []}

    dampen = CONFIG["STAR_IMPACT_DAMPENING"]
    max_boost = CONFIG["MAX_STAR_BOOST"]

    atk_boost = 1.0
    def_boost = 1.0

    for name, data in active.items():
        atk_boost += (data.get("attack", 1.0) - 1.0) * dampen
        def_boost += (data.get("defense", 1.0) - 1.0) * dampen

    atk_boost = min(atk_boost, max_boost)
    def_boost = min(def_boost, max_boost)

    return {
        "attack": round(atk_boost, 4),
        "defense": round(def_boost, 4),
        "players": list(active.keys()),
    }


# ──────────────────────────────────────────────
#  TEAM FORM STATISTICS (bug-fixed)
# ──────────────────────────────────────────────

def get_team_stats(team: str) -> dict:
    """
    Compute weighted attack/defense ratings from recent matches.
    Fixed: properly combines home+away, sorts by date, takes last N total.
    """
    df = _data.results
    global_gf = _data.global_avg["gf"]
    global_ga = _data.global_avg["ga"]
    last_n = CONFIG["LAST_N_MATCHES"]

    default = {
        "attack": 1.0, "defense": 1.0,
        "avg_gf": global_gf, "avg_ga": global_ga,
        "home_gf": global_gf, "away_gf": global_gf,
        "matches": 0,
        "weighted_gf": global_gf, "weighted_ga": global_ga,
    }

    if df.empty:
        return default

    # ── Combine home and away into unified match records ──
    home = df[df["home_team"] == team].copy()
    away = df[df["away_team"] == team].copy()

    if home.empty and away.empty:
        return default

    records = []

    for _, r in home.iterrows():
        records.append({
            "date": r.get("date"),
            "gf": r.get("home_score", 0),
            "ga": r.get("away_score", 0),
            "opponent": r.get("away_team", ""),
            "tournament": r.get("tournament", ""),
            "is_home": True,
        })

    for _, r in away.iterrows():
        records.append({
            "date": r.get("date"),
            "gf": r.get("away_score", 0),
            "ga": r.get("home_score", 0),
            "opponent": r.get("home_team", ""),
            "tournament": r.get("tournament", ""),
            "is_home": False,
        })

    # ── Sort by date, take LAST N matches total ──
    match_df = pd.DataFrame(records)
    if "date" in match_df.columns:
        match_df = match_df.sort_values("date", ascending=False)
    match_df = match_df.head(last_n)

    if match_df.empty:
        return default

    # ── Compute weighted averages ──
    weights = []
    for _, m in match_df.iterrows():
        opp_rank = get_team_ranking(m["opponent"])
        tw = time_weight(m["date"])
        tourney_w = tournament_weight(m["tournament"])
        opp_w = opponent_strength(opp_rank)
        weights.append(tw * tourney_w * opp_w)

    match_df["weight"] = weights
    total_w = match_df["weight"].sum()
    if total_w < 1e-6:
        total_w = 1.0

    weighted_gf = (match_df["gf"] * match_df["weight"]).sum() / total_w
    weighted_ga = (match_df["ga"] * match_df["weight"]).sum() / total_w

    n = len(match_df)
    gf_shrunk = shrink_to_global(weighted_gf, n, global_gf)
    ga_shrunk = shrink_to_global(weighted_ga, n, global_ga)

    attack = gf_shrunk / global_gf if global_gf > 0 else 1.0
    defense = ga_shrunk / global_ga if global_ga > 0 else 1.0

    # Simple averages for display
    avg_gf = match_df["gf"].mean()
    avg_ga = match_df["ga"].mean()

    home_matches = match_df[match_df["is_home"]]
    away_matches = match_df[~match_df["is_home"]]

    return {
        "attack": round(attack, 4),
        "defense": round(defense, 4),
        "avg_gf": round(avg_gf, 3),
        "avg_ga": round(avg_ga, 3),
        "home_gf": round(home_matches["gf"].mean(), 3) if len(home_matches) > 0 else global_gf,
        "away_gf": round(away_matches["gf"].mean(), 3) if len(away_matches) > 0 else global_gf,
        "matches": n,
        "weighted_gf": round(weighted_gf, 4),
        "weighted_ga": round(weighted_ga, 4),
    }


# ──────────────────────────────────────────────
#  DIXON-COLES SCORE MATRIX
# ──────────────────────────────────────────────

def dixon_coles_adjust(prob: float, i: int, j: int,
                       lam_a: float, lam_b: float, rho: float) -> float:
    """Low-score correlation adjustment (Dixon & Coles, 1997)."""
    if i == 0 and j == 0:
        return prob * (1.0 + rho * lam_a * lam_b)
    elif i == 0 and j == 1:
        return prob * (1.0 - rho * lam_a)
    elif i == 1 and j == 0:
        return prob * (1.0 - rho * lam_b)
    elif i == 1 and j == 1:
        return prob * (1.0 + rho)
    return prob


def build_score_matrix(lam_a: float, lam_b: float) -> np.ndarray:
    """Build normalized score probability matrix with DC correction."""
    max_g = CONFIG["MAX_GOALS"]
    rho = CONFIG["DIXON_COLES_RHO"]

    matrix = np.zeros((max_g + 1, max_g + 1))
    for i in range(max_g + 1):
        for j in range(max_g + 1):
            base = poisson.pmf(i, lam_a) * poisson.pmf(j, lam_b)
            matrix[i, j] = dixon_coles_adjust(base, i, j, lam_a, lam_b, rho)

    total = matrix.sum()
    if total > 0:
        matrix /= total

    return matrix


# ──────────────────────────────────────────────
#  MONTE CARLO SIMULATION (DC-consistent)
# ──────────────────────────────────────────────

def simulate_matches(matrix: np.ndarray, n_sims: int) -> dict:
    """
    Sample from the actual DC-corrected score matrix,
    NOT from plain Poisson. This keeps MC and analytical consistent.
    """
    max_g = matrix.shape[0]
    flat_probs = matrix.flatten()
    flat_probs = flat_probs / flat_probs.sum()  # ensure normalized

    indices = np.random.choice(len(flat_probs), size=n_sims, p=flat_probs)
    goals_a = indices // max_g
    goals_b = indices % max_g

    return {
        "goals_a": goals_a,
        "goals_b": goals_b,
        "wins_a": int((goals_a > goals_b).sum()),
        "draws": int((goals_a == goals_b).sum()),
        "wins_b": int((goals_a < goals_b).sum()),
    }


# ──────────────────────────────────────────────
#  LAMBDA CALCULATION (separated for clarity)
# ──────────────────────────────────────────────

def compute_lambdas(team_a: str, team_b: str,
                    stats_a: dict, stats_b: dict,
                    rank_a: int, rank_b: int,
                    star_a: dict, star_b: dict,
                    home: str = None) -> tuple[float, float]:
    """
    Compute expected goals (lambda) for each team.
    Blends form-based and ranking-based estimates.
    """
    global_gf = _data.global_avg["gf"]
    rf_a = ranking_factor(rank_a)
    rf_b = ranking_factor(rank_b)

    # ── Form-based lambdas ──
    lam_form_a = stats_a["attack"] * stats_b["defense"] * global_gf
    lam_form_b = stats_b["attack"] * stats_a["defense"] * global_gf

    # ── Ranking-based lambdas ──
    lam_rank_a = global_gf * rf_a / rf_b
    lam_rank_b = global_gf * rf_b / rf_a

    # ── Blend ──
    both_top = (rank_a <= CONFIG["TOP_TEAM_THRESHOLD"] and
                rank_b <= CONFIG["TOP_TEAM_THRESHOLD"])
    rw = CONFIG["RANK_WEIGHT_TOP"] if both_top else CONFIG["RANK_WEIGHT_OTHER"]
    fw = 1.0 - rw

    lam_a = rw * lam_rank_a + fw * lam_form_a
    lam_b = rw * lam_rank_b + fw * lam_form_b

    # ── Star player impact (relative, not absolute) ──
    avg_star_atk = (star_a["attack"] + star_b["attack"]) / 2
    avg_star_def = (star_a["defense"] + star_b["defense"]) / 2

    if avg_star_atk > 0:
        lam_a *= star_a["attack"] / avg_star_atk
        lam_b *= star_b["attack"] / avg_star_atk

    # Defensive stars reduce opponent's lambda
    if avg_star_def > 0:
        lam_a *= avg_star_def / star_b["defense"] if star_b["defense"] > 0 else 1.0
        lam_b *= avg_star_def / star_a["defense"] if star_a["defense"] > 0 else 1.0

    # ── Home advantage ──
    if home == team_a:
        lam_a *= CONFIG["HOME_ATTACK_BOOST"]
        lam_b *= CONFIG["HOME_DEFENSE_BOOST"]
    elif home == team_b:
        lam_b *= CONFIG["HOME_ATTACK_BOOST"]
        lam_a *= CONFIG["HOME_DEFENSE_BOOST"]

    # ── Cap ratio for top team matchups ──
    if both_top:
        max_ratio = CONFIG["MAX_LAMBDA_RATIO_TOP"]
        ratio = lam_a / lam_b if lam_b > 0 else 1.0
        if ratio > max_ratio:
            lam_a = lam_b * max_ratio
        elif ratio < 1.0 / max_ratio:
            lam_b = lam_a * max_ratio

    # ── Floor ──
    lam_a = max(lam_a, CONFIG["MIN_LAMBDA"])
    lam_b = max(lam_b, CONFIG["MIN_LAMBDA"])

    return round(lam_a, 4), round(lam_b, 4)


# ──────────────────────────────────────────────
#  MATCH TYPE CLASSIFICATION
# ──────────────────────────────────────────────

def classify_match(rank_a: int, rank_b: int) -> str:
    gap = abs(rank_a - rank_b)
    both_top = rank_a <= CONFIG["TOP_TEAM_THRESHOLD"] and rank_b <= CONFIG["TOP_TEAM_THRESHOLD"]

    if both_top and gap < 20:
        return "⚔️ Elite Clash"
    elif gap > 100:
        return "🔻 Total Mismatch"
    elif gap > 50:
        return "📊 Clear Favorite"
    elif both_top:
        return "🔥 Top Team Showdown"
    else:
        return "⚡ Competitive Match"


# ──────────────────────────────────────────────
#  MAIN PREDICTION FUNCTION
# ──────────────────────────────────────────────

def predict(team_a: str, team_b: str, home: str = None) -> dict:
    """
    Generate a full match prediction for team_a vs team_b.

    Args:
        team_a: First team name (must match dataset)
        team_b: Second team name
        home: Name of the home team (or None for neutral)

    Returns:
        Dictionary with probabilities, lambdas, top scores,
        simulation data, and metadata.
    """
    # ── Gather data ──
    stats_a = get_team_stats(team_a)
    stats_b = get_team_stats(team_b)
    rank_a = get_team_ranking(team_a)
    rank_b = get_team_ranking(team_b)
    points_a = get_team_points(team_a)
    points_b = get_team_points(team_b)
    star_a = get_team_star_impact(team_a)
    star_b = get_team_star_impact(team_b)

    # ── Compute expected goals ──
    lam_a, lam_b = compute_lambdas(
        team_a, team_b, stats_a, stats_b,
        rank_a, rank_b, star_a, star_b, home
    )

    # ── Build score matrix (analytical) ──
    matrix = build_score_matrix(lam_a, lam_b)
    max_g = CONFIG["MAX_GOALS"]

    # ── Extract probabilities ──
    win_a = sum(matrix[i, j] for i in range(max_g+1) for j in range(max_g+1) if i > j)
    draw  = sum(matrix[i, j] for i in range(max_g+1) for j in range(max_g+1) if i == j)
    win_b = sum(matrix[i, j] for i in range(max_g+1) for j in range(max_g+1) if i < j)

    # ── Top predicted scorelines ──
    score_probs = {}
    for i in range(max_g + 1):
        for j in range(max_g + 1):
            score_probs[f"{i}-{j}"] = float(matrix[i, j])

    top_scores = sorted(score_probs.items(), key=lambda x: -x[1])[:10]
    top_scores_display = [(s, round(p * 100, 2)) for s, p in top_scores]  # actual %

    # ── Monte Carlo (DC-consistent) ──
    n_sims = CONFIG["N_SIMULATIONS"]
    sim = simulate_matches(matrix, n_sims)

    # ── Confidence check: analytical vs simulation ──
    sim_win_a_pct = round(100 * sim["wins_a"] / n_sims, 1)
    sim_draw_pct = round(100 * sim["draws"] / n_sims, 1)
    sim_win_b_pct = round(100 * sim["wins_b"] / n_sims, 1)

    return {
        # Teams
        "team_a": team_a,
        "team_b": team_b,

        # Analytical probabilities
        "team_a_win": round(100 * win_a, 1),
        "draw": round(100 * draw, 1),
        "team_b_win": round(100 * win_b, 1),

        # Simulation probabilities (for cross-validation display)
        "sim_team_a_win": sim_win_a_pct,
        "sim_draw": sim_draw_pct,
        "sim_team_b_win": sim_win_b_pct,

        # Expected goals
        "team_a_lambda": lam_a,
        "team_b_lambda": lam_b,

        # Rankings
        "team_a_rank": rank_a,
        "team_b_rank": rank_b,
        "team_a_points": points_a,
        "team_b_points": points_b,

        # Star players
        "team_a_stars": star_a["players"],
        "team_b_stars": star_b["players"],
        "team_a_star_boost": star_a["attack"],
        "team_b_star_boost": star_b["attack"],
        "team_a_def_boost": star_a["defense"],
        "team_b_def_boost": star_b["defense"],

        # Form stats
        "team_a_attack": stats_a["attack"],
        "team_a_defense": stats_a["defense"],
        "team_b_attack": stats_b["attack"],
        "team_b_defense": stats_b["defense"],

        # Match metadata
        "match_type": classify_match(rank_a, rank_b),
        "rank_gap": abs(rank_a - rank_b),
        "home": home,

        # Scorelines (% not fake simulation counts)
        "top_scores": top_scores_display,
        "score_matrix": matrix,

        # Simulation arrays (for histograms in charts)
        "goals_a": sim["goals_a"],
        "goals_b": sim["goals_b"],
        "n_simulations": n_sims,
    }


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  MUNDIALISTA AI — Prediction Engine v7")
    print("=" * 55)

    result = predict("Argentina", "Brazil")

    print(f"\n  {result['team_a']} vs {result['team_b']}")
    print(f"  Type: {result['match_type']}")
    print(f"  Ranks: #{result['team_a_rank']} vs #{result['team_b_rank']}")
    print(f"\n  ┌─────────────────────────────────────┐")
    print(f"  │  Win: {result['team_a_win']:5.1f}%  │  Draw: {result['draw']:5.1f}%  │  Win: {result['team_b_win']:5.1f}%  │")
    print(f"  └─────────────────────────────────────┘")
    print(f"  Expected Goals: {result['team_a_lambda']:.2f} vs {result['team_b_lambda']:.2f}")
    print(f"  Attack/Defense: {result['team_a_attack']:.3f}/{result['team_a_defense']:.3f}"
          f"  vs  {result['team_b_attack']:.3f}/{result['team_b_defense']:.3f}")
    print(f"\n  Simulation cross-check ({result['n_simulations']:,} runs):")
    print(f"  Win: {result['sim_team_a_win']}% | Draw: {result['sim_draw']}% | Win: {result['sim_team_b_win']}%")
    print(f"\n  Top Predicted Scorelines:")
    for score, pct in result["top_scores"][:5]:
        print(f"    {score:>5s}  →  {pct:.1f}%")
    print()