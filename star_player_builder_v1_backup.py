"""
Mundialista AI — Star Player Builder
Generates data-driven star player ratings from goalscorers.csv

Instead of hardcoding "Messi = 1.15", this calculates impact from
REAL international scoring records with:
  - Time decay (recent goals matter more)
  - Tournament weighting (World Cup goal > Friendly goal)
  - Opponent strength (goal vs Brazil > goal vs Andorra)
  - Penalty discount (penalties count less)
  - Own goal exclusion
  - Per-match normalization

Usage:
    python star_player_builder.py
    -> Creates data/star_players.json
    -> prediction_engine.py v7 auto-loads it
"""

import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


# ──────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────

BUILDER_CONFIG = {
    "YEARS_BACK": 4,
    "PENALTY_DISCOUNT": 0.60,
    "TIME_DECAY_RATE": 0.0015,
    "MIN_GOALS_STAR": 4,
    "MIN_GOALS_ELITE": 8,
    "MAX_STARS_PER_TEAM": 5,
    "BOOST_SCALE": 0.18,
    "MIN_BOOST": 1.00,
    "MAX_BOOST": 1.22,
    "TOURNAMENT_WEIGHTS": {
        "fifa world cup": 1.0,
        "copa america": 0.90,
        "uefa euro": 0.90,
        "africa cup of nations": 0.85,
        "afc asian cup": 0.85,
        "concacaf gold cup": 0.80,
        "concacaf nations league": 0.80,
        "uefa nations league": 0.85,
        "fifa world cup qualification": 0.80,
        "friendly": 0.45,
    },
    "DEFAULT_TOURNAMENT_WEIGHT": 0.60,
    "DEFENSIVE_OVERRIDES": {
        "Argentina": {
            "Emiliano Martinez": {"defense": 1.08, "role": "GK"},
        },
        "France": {
            "Mike Maignan":       {"defense": 1.06, "role": "GK"},
            "William Saliba":     {"defense": 1.05, "role": "CB"},
        },
        "England": {
            "Jordan Pickford":    {"defense": 1.04, "role": "GK"},
            "John Stones":        {"defense": 1.04, "role": "CB"},
        },
        "Spain": {
            "Rodri":              {"defense": 1.08, "role": "DM"},
            "Unai Simon":         {"defense": 1.04, "role": "GK"},
        },
        "Germany": {
            "Antonio Rudiger":    {"defense": 1.06, "role": "CB"},
            "Manuel Neuer":       {"defense": 1.04, "role": "GK"},
        },
        "Italy": {
            "Gianluigi Donnarumma": {"defense": 1.07, "role": "GK"},
        },
        "Portugal": {
            "Ruben Dias":         {"defense": 1.06, "role": "CB"},
            "Diogo Costa":        {"defense": 1.04, "role": "GK"},
        },
        "Netherlands": {
            "Virgil van Dijk":    {"defense": 1.10, "role": "CB"},
        },
        "Brazil": {
            "Alisson Becker":     {"defense": 1.07, "role": "GK"},
            "Marquinhos":         {"defense": 1.05, "role": "CB"},
        },
        "Croatia": {
            "Dominik Livakovic":  {"defense": 1.05, "role": "GK"},
        },
        "Morocco": {
            "Yassine Bounou":     {"defense": 1.06, "role": "GK"},
            "Achraf Hakimi":      {"defense": 1.06, "role": "RB"},
        },
        "Uruguay": {
            "Federico Valverde":  {"defense": 1.04, "role": "CM"},
        },
        "Belgium": {
            "Thibaut Courtois":   {"defense": 1.07, "role": "GK"},
        },
        "Senegal": {
            "Kalidou Koulibaly":  {"defense": 1.06, "role": "CB"},
        },
        "United States": {
            "Matt Turner":        {"defense": 1.03, "role": "GK"},
        },
    },
}


def load_rankings_dict():
    try:
        df = pd.read_csv("data/rankings.csv")
        return dict(zip(df["country_full"], df["rank"]))
    except (FileNotFoundError, KeyError):
        return {}


def ranking_factor(rank):
    return 1.0 + 0.10 * math.log(201.0 / max(rank, 1))


def opponent_strength_weight(opponent_rank):
    return ranking_factor(opponent_rank) / ranking_factor(50)


def get_tournament_weight(tournament_name):
    if not isinstance(tournament_name, str):
        return BUILDER_CONFIG["DEFAULT_TOURNAMENT_WEIGHT"]
    t_lower = tournament_name.lower()
    for key, val in BUILDER_CONFIG["TOURNAMENT_WEIGHTS"].items():
        if key in t_lower:
            return val
    return BUILDER_CONFIG["DEFAULT_TOURNAMENT_WEIGHT"]


def build_star_players(verbose=True):
    cfg = BUILDER_CONFIG

    gs = pd.read_csv("data/goalscorers.csv")
    rs = pd.read_csv("data/results.csv")

    gs["date"] = pd.to_datetime(gs["date"], errors="coerce")
    rs["date"] = pd.to_datetime(rs["date"], errors="coerce")

    rankings = load_rankings_dict()

    cutoff = datetime.now() - pd.Timedelta(days=cfg["YEARS_BACK"] * 365)
    gs_recent = gs[gs["date"] >= cutoff].copy()
    rs_recent = rs[rs["date"] >= cutoff].copy()

    if verbose:
        print(f"Analysis window: {cutoff.strftime('%Y-%m-%d')} to present")
        print(f"Goals in window: {len(gs_recent):,}")
        print(f"Matches in window: {len(rs_recent):,}")
        print()

    if "own_goal" in gs_recent.columns:
        own_goals = gs_recent["own_goal"].sum()
        gs_recent = gs_recent[gs_recent["own_goal"] != True].copy()
        if verbose:
            print(f"Excluded {int(own_goals)} own goals")

    home_counts = rs_recent.groupby("home_team").size()
    away_counts = rs_recent.groupby("away_team").size()
    team_matches = (home_counts.add(away_counts, fill_value=0)).to_dict()

    rs_tourney = rs_recent[["date", "home_team", "away_team", "tournament"]].drop_duplicates()
    gs_merged = gs_recent.merge(
        rs_tourney,
        on=["date", "home_team", "away_team"],
        how="left",
    )

    gs_merged["opponent"] = gs_merged.apply(
        lambda row: row["away_team"] if row["team"] == row["home_team"] else row["home_team"],
        axis=1,
    )

    now = datetime.now()

    def calc_goal_weight(row):
        days_ago = max(0, (now - row["date"]).days)
        time_w = math.exp(-cfg["TIME_DECAY_RATE"] * days_ago)
        tourney_w = get_tournament_weight(row.get("tournament", ""))
        opp_rank = rankings.get(row["opponent"], 100)
        opp_w = opponent_strength_weight(opp_rank)
        penalty_w = cfg["PENALTY_DISCOUNT"] if row.get("penalty", False) else 1.0
        return time_w * tourney_w * opp_w * penalty_w

    gs_merged["goal_weight"] = gs_merged.apply(calc_goal_weight, axis=1)

    if verbose:
        print(f"Weighted {len(gs_merged):,} goals")
        print()

    player_stats = (
        gs_merged
        .groupby(["scorer", "team"])
        .agg(
            raw_goals=("goal_weight", "size"),
            weighted_goals=("goal_weight", "sum"),
            penalty_goals=("penalty", "sum"),
            last_goal=("date", "max"),
            first_goal=("date", "min"),
        )
        .reset_index()
    )

    player_stats["team_matches"] = (
        player_stats["team"].map(team_matches).fillna(1).astype(float)
    )
    player_stats["goals_per_match"] = player_stats["raw_goals"] / player_stats["team_matches"]
    player_stats["weighted_gpm"] = player_stats["weighted_goals"] / player_stats["team_matches"]

    stars = player_stats[player_stats["raw_goals"] >= cfg["MIN_GOALS_STAR"]].copy()

    if verbose:
        print(f"Players meeting minimum ({cfg['MIN_GOALS_STAR']}+ goals): {len(stars)}")

    global_median_wgpm = stars["weighted_gpm"].median()

    if verbose:
        print(f"Global median weighted goals/match: {global_median_wgpm:.4f}")
        print()

    def calc_attack_boost(row):
        if global_median_wgpm <= 0:
            return 1.0
        relative = (row["weighted_gpm"] - global_median_wgpm) / global_median_wgpm
        boost = 1.0 + cfg["BOOST_SCALE"] * relative
        if row["raw_goals"] >= cfg["MIN_GOALS_ELITE"]:
            boost += 0.01
        return round(max(cfg["MIN_BOOST"], min(cfg["MAX_BOOST"], boost)), 3)

    stars["attack_boost"] = stars.apply(calc_attack_boost, axis=1)

    star_dict = {}

    for team_name, group in stars.groupby("team"):
        top_players = group.nlargest(cfg["MAX_STARS_PER_TEAM"], "weighted_goals")
        team_entry = {}
        for _, row in top_players.iterrows():
            player_name = row["scorer"]
            team_entry[player_name] = {
                "attack": float(row["attack_boost"]),
                "defense": 1.0,
                "status": "active",
                "data_source": "goalscorers.csv",
                "goals": int(row["raw_goals"]),
                "penalties": int(row["penalty_goals"]),
                "weighted_goals": round(float(row["weighted_goals"]), 2),
                "goals_per_match": round(float(row["goals_per_match"]), 4),
                "last_goal": str(row["last_goal"])[:10],
            }
        if team_entry:
            star_dict[team_name] = team_entry

    defensive = cfg["DEFENSIVE_OVERRIDES"]
    for team_name, players in defensive.items():
        if team_name not in star_dict:
            star_dict[team_name] = {}
        for player_name, data in players.items():
            if player_name in star_dict[team_name]:
                star_dict[team_name][player_name]["defense"] = data["defense"]
                star_dict[team_name][player_name]["role"] = data.get("role", "")
            else:
                star_dict[team_name][player_name] = {
                    "attack": 1.0,
                    "defense": data["defense"],
                    "status": "active",
                    "data_source": "manual_override",
                    "role": data.get("role", "DEF"),
                    "goals": 0,
                }

    star_dict = dict(sorted(star_dict.items()))

    if verbose:
        print(f"Total teams with star players: {len(star_dict)}")
        total_players = sum(len(v) for v in star_dict.values())
        print(f"Total star players: {total_players}")

    return star_dict


def save_star_players(star_dict, path="data/star_players.json"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(star_dict, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {path}")
    print(f"   File size: {Path(path).stat().st_size:,} bytes")


def print_top_stars(star_dict, top_n=30):
    all_stars = []
    for team, players in star_dict.items():
        for player, data in players.items():
            all_stars.append({
                "player": player,
                "team": team,
                "attack": data.get("attack", 1.0),
                "defense": data.get("defense", 1.0),
                "goals": data.get("goals", 0),
                "source": data.get("data_source", "unknown"),
            })

    all_stars.sort(key=lambda x: x["attack"], reverse=True)

    print(f"\n{'='*70}")
    print(f"  TOP {top_n} STAR PLAYERS BY ATTACK RATING")
    print(f"{'='*70}")
    print(f"  {'#':>3}  {'Player':<25} {'Team':<18} {'ATK':>5} {'DEF':>5} {'Goals':>5}")
    print(f"  {'---':>3}  {'---':<25} {'---':<18} {'---':>5} {'---':>5} {'---':>5}")

    for i, s in enumerate(all_stars[:top_n], 1):
        atk = f"{s['attack']:.2f}" if s["attack"] > 1.0 else " --"
        def_ = f"{s['defense']:.2f}" if s["defense"] > 1.0 else " --"
        print(f"  {i:>3}. {s['player']:<25} {s['team']:<18} {atk:>5} {def_:>5} {s['goals']:>5}")


def print_team_report(star_dict, team):
    if team not in star_dict:
        print(f"  No star data for {team}")
        return

    print(f"\n  --- {team} ---")
    players = star_dict[team]
    for name, data in sorted(players.items(), key=lambda x: -x[1].get("attack", 1.0)):
        atk = data.get("attack", 1.0)
        def_ = data.get("defense", 1.0)
        goals = data.get("goals", 0)
        role = data.get("role", "")

        atk_str = f"ATK {atk:.2f}" if atk > 1.0 else "        "
        def_str = f"DEF {def_:.2f}" if def_ > 1.0 else "        "
        goal_str = f"({goals} goals)" if goals > 0 else f"({role})"

        print(f"  | {name:<25} {atk_str}  {def_str}  {goal_str}")
    print(f"  {'─' * 50}")


if __name__ == "__main__":
    print("=" * 60)
    print("  MUNDIALISTA AI — Star Player Builder")
    print("=" * 60)
    print()

    star_dict = build_star_players(verbose=True)

    save_star_players(star_dict)

    print_top_stars(star_dict, top_n=30)

    print()
    print("=" * 60)
    print("  KEY TEAM REPORTS")
    print("=" * 60)
    for team in ["Argentina", "France", "Brazil", "England", "Spain",
                 "Germany", "Portugal", "Netherlands", "Norway", "Sweden",
                 "United States", "Mexico", "Morocco", "Japan"]:
        print_team_report(star_dict, team)

    print()
    print("Done! prediction_engine.py v7 will auto-load data/star_players.json")
    print("   Re-run anytime to update ratings with latest match data.")
