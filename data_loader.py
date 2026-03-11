"""
data_loader.py — Data layer for Mundialista Network AI
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from pathlib import Path

DATA_DIR = Path("data")
RESULTS_FILE = DATA_DIR / "results.csv"
GOALSCORERS_FILE = DATA_DIR / "goalscorers.csv"
RANKINGS_FILE = DATA_DIR / "rankings.csv"

DEFAULT_YEARS_LOOKBACK = 4
DEFAULT_LAST_N_MATCHES = 7
DEFAULT_H2H_YEARS = 10


def _safe_mean(arr, default=1.0):
    if arr is None or len(arr) == 0:
        return default
    return float(np.mean(arr))

def _safe_std(arr, default=0.5):
    if arr is None or len(arr) < 2:
        return default
    return float(np.std(arr))


def load_results(years_lookback=DEFAULT_YEARS_LOOKBACK):
    if RESULTS_FILE.exists():
        df = pd.read_csv(RESULTS_FILE, parse_dates=["date"])
    elif RESULTS_FILE.with_suffix(".csv.gz").exists():
        df = pd.read_csv(RESULTS_FILE.with_suffix(".csv.gz"),
                         parse_dates=["date"], compression="gzip")
    else:
        raise FileNotFoundError(f"Cannot find {RESULTS_FILE}")
    cutoff = pd.Timestamp.now() - pd.DateOffset(years=years_lookback)
    df = df[df["date"] >= cutoff].copy()
    df = df.sort_values("date", ascending=False).reset_index(drop=True)
    print(f"Loaded {len(df):,} matches")
    return df


def load_goalscorers():
    df = pd.read_csv(GOALSCORERS_FILE)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_rankings():
    df = pd.read_csv(RANKINGS_FILE, parse_dates=["rank_date"])
    return df


def get_latest_rankings():
    rankings = load_rankings()
    latest_date = rankings["rank_date"].max()
    latest = rankings[rankings["rank_date"] == latest_date].copy()
    return latest.sort_values("rank").reset_index(drop=True)


def get_all_teams(results):
    teams = set(results["home_team"].unique()) | set(results["away_team"].unique())
    return sorted(teams)


def get_team_matches(results, team):
    home = results[results["home_team"] == team].copy()
    home = home.assign(team=team, opponent=home["away_team"],
                       goals_for=home["home_score"],
                       goals_against=home["away_score"], is_home=1)
    away = results[results["away_team"] == team].copy()
    away = away.assign(team=team, opponent=away["home_team"],
                       goals_for=away["away_score"],
                       goals_against=away["home_score"], is_home=0)
    combined = pd.concat([home, away], ignore_index=True)
    return combined.sort_values("date", ascending=False).reset_index(drop=True)


def get_team_stats(results, team, opponent,
                   last_n=DEFAULT_LAST_N_MATCHES,
                   h2h_years=DEFAULT_H2H_YEARS):
    team_df = get_team_matches(results, team)
    if len(team_df) == 0:
        return {"avg_gf":1.0,"avg_ga":1.0,"std_gf":0.5,"std_ga":0.5,
                "n_matches":0,"form_gf":1.0,"form_ga":1.0,"form_n":0,
                "h2h_gf":None,"h2h_ga":None,"h2h_n":0,
                "home_pct":0.5,"competitive_pct":0.5}
    non_h2h = team_df[team_df["opponent"] != opponent]
    last_n_df = non_h2h.head(last_n)
    h2h_cutoff = pd.Timestamp.now() - pd.DateOffset(years=h2h_years)
    h2h_df = team_df[(team_df["opponent"]==opponent) & (team_df["date"]>=h2h_cutoff)]
    combined_gf = np.concatenate([last_n_df["goals_for"].values, h2h_df["goals_for"].values])
    combined_ga = np.concatenate([last_n_df["goals_against"].values, h2h_df["goals_against"].values])
    friendly = ["Friendly","friendly"]
    is_comp = ~last_n_df["tournament"].str.contains("|".join(friendly), case=False, na=False) if len(last_n_df)>0 else pd.Series([True])
    return {
        "avg_gf": _safe_mean(combined_gf),
        "avg_ga": _safe_mean(combined_ga),
        "std_gf": _safe_std(combined_gf),
        "std_ga": _safe_std(combined_ga),
        "n_matches": len(combined_gf),
        "form_gf": _safe_mean(last_n_df["goals_for"]),
        "form_ga": _safe_mean(last_n_df["goals_against"]),
        "form_n": len(last_n_df),
        "h2h_gf": _safe_mean(h2h_df["goals_for"], default=None),
        "h2h_ga": _safe_mean(h2h_df["goals_against"], default=None),
        "h2h_n": len(h2h_df),
        "home_pct": _safe_mean(last_n_df["is_home"], default=0.5),
        "competitive_pct": float(is_comp.mean()),
    }


def get_team_ranking(team, rankings_df=None):
    if rankings_df is None:
        try:
            rankings_df = get_latest_rankings()
        except FileNotFoundError:
            return {"rank": 100, "total_points": 1000.0}
    match = rankings_df[rankings_df["country_full"].str.lower() == team.lower()]
    if len(match) > 0:
        row = match.iloc[0]
        return {"rank": int(row["rank"]), "total_points": float(row["total_points"])}
    return {"rank": 150, "total_points": 800.0}


def analyze_goal_timing(team=None):
    try:
        scorers = load_goalscorers()
    except FileNotFoundError:
        return {"first_half_pct":0.45,"second_half_pct":0.55,
                "min_0_15_pct":0.15,"min_15_45_pct":0.30,
                "min_45_60_pct":0.18,"min_60_80_pct":0.22,
                "min_80_90_pct":0.15,"mean_minute":48.0,
                "median_minute":49.0,"total_goals_analyzed":0}
    if team: scorers = scorers[scorers["team"]==team]
    if len(scorers)==0:
        return {"total_goals_analyzed":0}
    minutes = scorers["minute"].dropna()
    minutes = minutes[minutes<=90]
    total = len(minutes)
    if total==0:
        return {"total_goals_analyzed":0}
    return {
        "first_half_pct": float((minutes<=45).sum()/total),
        "second_half_pct": float((minutes>45).sum()/total),
        "min_0_15_pct": float(((minutes>=0)&(minutes<=15)).sum()/total),
        "min_15_45_pct": float(((minutes>15)&(minutes<=45)).sum()/total),
        "min_45_60_pct": float(((minutes>45)&(minutes<=60)).sum()/total),
        "min_60_80_pct": float(((minutes>60)&(minutes<=80)).sum()/total),
        "min_80_90_pct": float((minutes>80).sum()/total),
        "mean_minute": float(minutes.mean()),
        "median_minute": float(minutes.median()),
        "total_goals_analyzed": total,
    }


def compute_empirical_lambda_multipliers(team=None):
    timing = analyze_goal_timing(team)
    if timing.get("total_goals_analyzed",0) < 100:
        return {"min_0_15":0.85,"min_15_45":1.00,
                "min_45_60":1.10,"min_60_80":1.05,"min_80_90":1.30}
    periods = {
        "min_0_15":(timing["min_0_15_pct"],15),
        "min_15_45":(timing["min_15_45_pct"],30),
        "min_45_60":(timing["min_45_60_pct"],15),
        "min_60_80":(timing["min_60_80_pct"],20),
        "min_80_90":(timing["min_80_90_pct"],10),
    }
    mult = {}
    for name,(pct,dur) in periods.items():
        mult[name] = (pct/dur) / (1.0/90.0)
    check = sum(mult[p]*periods[p][1] for p in mult)
    if abs(check-90.0) > 0.01:
        factor = 90.0/check
        mult = {k:v*factor for k,v in mult.items()}
    return mult
# ─────────────────────────────────────────────────────────────
# ALIAS MAP: TEAM_DATABASE names → CSV names
# ─────────────────────────────────────────────────────────────
TEAM_NAME_ALIASES = {
    "USA": "United States",
    "Bosnia": "Bosnia and Herzegovina",
    "UAE": "United Arab Emirates",
}


def resolve_team_name(name: str, available_teams: list) -> str:
    """Resolve a team name to match CSV conventions."""
    # Exact match
    if name in available_teams:
        return name
    # Alias match
    if name in TEAM_NAME_ALIASES:
        alias = TEAM_NAME_ALIASES[name]
        if alias in available_teams:
            return alias
    # Case-insensitive match
    lower_map = {t.lower(): t for t in available_teams}
    if name.lower() in lower_map:
        return lower_map[name.lower()]
    # Partial match
    for t in available_teams:
        if name.lower() in t.lower() or t.lower() in name.lower():
            return t
    return name  # Return as-is, will get no matches



def _tournament_weight(tournament_name):
    """Return importance weight for a tournament type."""
    if tournament_name is None:
        return 1.0
    t = str(tournament_name).lower()
    # World Cup and qualifiers
    if "world cup" in t and "qualification" not in t:
        return 1.5
    if "world cup qualification" in t or "world cup qualifier" in t:
        return 1.5
    # Continental championships
    if any(comp in t for comp in ["copa am", "euro ", "european championship",
                                   "afcon", "africa cup", "african cup",
                                   "asian cup", "gold cup", "concacaf championship",
                                   "ofc nations"]):
        return 1.3
    # Continental qualifiers
    if "qualification" in t and any(comp in t for comp in ["euro", "africa", "asian", "copa"]):
        return 1.3
    # Nations leagues
    if "nations league" in t:
        return 1.2
    # Confederations cup, intercontinental
    if any(comp in t for comp in ["confederations", "intercontinental",
                                   "finalissima", "copa centenario"]):
        return 1.3
    # Friendlies
    if "friendly" in t or "fifa series" in t:
        return 0.7
    # Everything else (minor tournaments, regional cups)
    return 1.0


def get_team_stats_for_app(results, team, opponent, last_n=40):
    """
    Get team stats with tournament weighting.
    Competitive matches count more than friendlies.
    """
    matches = get_team_matches(results, team)
    if len(matches) == 0:
        return None

    # Get last N matches
    matches = matches.tail(last_n).copy()

    # Calculate tournament weights
    matches["weight"] = matches["tournament"].apply(_tournament_weight)

    gf = matches["goals_for"].values.astype(float)
    ga = matches["goals_against"].values.astype(float)
    weights = matches["weight"].values.astype(float)

    # Weighted averages
    total_weight = weights.sum()
    if total_weight == 0:
        total_weight = 1.0

    avg_gf = float(np.sum(gf * weights) / total_weight)
    avg_ga = float(np.sum(ga * weights) / total_weight)

    # Weighted standard deviation
    mean_gf = avg_gf
    mean_ga = avg_ga
    std_gf = float(np.sqrt(np.sum(weights * (gf - mean_gf) ** 2) / total_weight))
    std_ga = float(np.sqrt(np.sum(weights * (ga - mean_ga) ** 2) / total_weight))
    std_gf = max(std_gf, 0.3)
    std_ga = max(std_ga, 0.3)

    n_matches = len(matches)

    # Head-to-head
    h2h = matches[matches["opponent"] == opponent] if "opponent" in matches.columns else None
    if h2h is not None and len(h2h) > 0:
        h2h_gf = float(h2h["goals_for"].mean())
        h2h_ga = float(h2h["goals_against"].mean())
        h2h_n = len(h2h)
    else:
        h2h_gf = None
        h2h_ga = None
        h2h_n = 0

    # Competitive match percentage
    comp_count = len(matches[matches["weight"] >= 1.0])
    competitive_pct = comp_count / n_matches if n_matches > 0 else 0.0

    # Recent form (last 10, also weighted)
    recent = matches.tail(10)
    recent_w = recent["weight"].values.astype(float)
    recent_gf = recent["goals_for"].values.astype(float)
    recent_ga = recent["goals_against"].values.astype(float)
    rw_total = recent_w.sum() if recent_w.sum() > 0 else 1.0
    form_gf = float(np.sum(recent_gf * recent_w) / rw_total)
    form_ga = float(np.sum(recent_ga * recent_w) / rw_total)

    return {
        "avg_gf": avg_gf,
        "avg_ga": avg_ga,
        "std_gf": std_gf,
        "std_ga": std_ga,
        "n_matches": n_matches,
        "goals_for": matches["goals_for"].values,
        "goals_against": matches["goals_against"].values,
        "found": True,
        "h2h_gf": h2h_gf,
        "h2h_ga": h2h_ga,
        "h2h_n": h2h_n,
        "competitive_pct": competitive_pct,
        "form_gf": form_gf,
        "form_ga": form_ga,
    }
