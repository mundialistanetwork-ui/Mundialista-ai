# star_player_builder_v2.py — Mundialista AI Star Player Builder v2
# Generates 2 attackers + 2 defenders per team with percentile-based tiers
# Author: Mundialista AI Team | June 2025

import pandas as pd
import numpy as np
import json
import unicodedata
import shutil
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"

CONFIG = {
    # Attack tiers (percentile thresholds -> boost ranges)
    "ELITE_PERCENTILE": 95,    # top 5%  -> 1.25 - 1.35
    "STAR_PERCENTILE": 85,     # top 15% -> 1.15 - 1.25
    "KEY_PERCENTILE": 70,      # top 30% -> 1.08 - 1.15

    # Defense boost range
    "DEF_BOOST_MIN": 1.03,
    "DEF_BOOST_MAX": 1.12,

    # Filters
    "MIN_GOALS": 4,
    "MIN_MATCHES_DEFENSE": 10,
    "RECENT_YEARS": 4,
    "ATTACKERS_PER_TEAM": 2,
    "DEFENDERS_PER_TEAM": 2,

    # Time decay
    "DECAY_HALFLIFE_YEARS": 2.0,

    # Tournament weights
    "TOURNAMENT_WEIGHTS": {
        "FIFA World Cup": 3.0,
        "FIFA World Cup qualification": 2.0,
        "Copa America": 2.0,
        "UEFA Euro": 2.0,
        "UEFA Euro qualification": 1.5,
        "AFC Asian Cup": 1.8,
        "Africa Cup of Nations": 1.8,
        "UEFA Nations League": 1.5,
        "CONMEBOL-UEFA Cup of Champions": 1.5,
        "Friendly": 0.7,
    },
}


# === UNICODE NORMALIZATION ===

def normalize_name(name: str) -> str:
    """Normalize unicode to prevent duplicates like Alvarez vs Alvarez."""
    if not isinstance(name, str):
        return str(name)
    normalized = unicodedata.normalize("NFC", name.strip())
    return normalized


def deduplicate_players(players: list) -> list:
    """Remove duplicate players by normalized name."""
    seen = set()
    unique = []
    for p in players:
        key = normalize_name(p["name"]).lower()
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


# === ATTACK SCORING ===

def compute_attack_scores(goalscorers, results):
    """
    Compute weighted goal score per player.
    Weights: time decay x tournament importance x penalty discount.
    Merges tournament info from results.csv since goalscorers.csv lacks it.
    """
    now = datetime.now()
    cutoff = now - pd.DateOffset(years=CONFIG["RECENT_YEARS"])

    gs = goalscorers.copy()
    gs["date"] = pd.to_datetime(gs["date"], errors="coerce")
    gs = gs[gs["date"] >= cutoff].dropna(subset=["date"])

    if gs.empty:
        print("[WARN] No recent goals found.")
        return pd.DataFrame()

    # Merge tournament from results
    res = results[["date", "home_team", "away_team", "tournament"]].copy()
    res["date"] = pd.to_datetime(res["date"], errors="coerce")
    gs = gs.merge(res, on=["date", "home_team", "away_team"], how="left")

    # Time decay
    days_ago = (now - gs["date"]).dt.days
    gs["time_weight"] = np.exp(-np.log(2) * days_ago / (CONFIG["DECAY_HALFLIFE_YEARS"] * 365.25))

    # Tournament weight
    gs["tourn_weight"] = gs["tournament"].map(CONFIG["TOURNAMENT_WEIGHTS"]).fillna(1.0)

    # Penalty discount
    gs["penalty_discount"] = gs["penalty"].apply(lambda x: 0.5 if x else 1.0)

    # Weighted goal value
    gs["goal_value"] = gs["time_weight"] * gs["tourn_weight"] * gs["penalty_discount"]

    # Aggregate per player per team
    player_scores = gs.groupby(["team", "scorer"]).agg(
        total_weighted_goals=("goal_value", "sum"),
        raw_goals=("scorer", "count"),
    ).reset_index()

    player_scores.rename(columns={"scorer": "name"}, inplace=True)

    # Filter minimum goals
    player_scores = player_scores[player_scores["raw_goals"] >= CONFIG["MIN_GOALS"]]

    print(f"[INFO] Computed attack scores for {len(player_scores)} players across {player_scores['team'].nunique()} teams")

    return player_scores


# === PERCENTILE TIER SYSTEM ===

def assign_attack_tier(score, elite_cutoff, star_cutoff, key_cutoff):
    """
    Assign tier and boost based on percentile cutoffs.
    Elite: 1.25-1.35 | Star: 1.15-1.25 | Key: 1.08-1.15 | Base: 1.00
    """
    if score >= elite_cutoff:
        ratio = min((score - elite_cutoff) / max(elite_cutoff * 0.5, 0.01), 1.0)
        boost = 1.25 + (0.10 * ratio)
        return {"tier": "elite", "label": "Elite", "boost": round(boost, 3)}

    elif score >= star_cutoff:
        ratio = (score - star_cutoff) / max(elite_cutoff - star_cutoff, 0.01)
        boost = 1.15 + (0.10 * ratio)
        return {"tier": "star", "label": "Star", "boost": round(boost, 3)}

    elif score >= key_cutoff:
        ratio = (score - key_cutoff) / max(star_cutoff - key_cutoff, 0.01)
        boost = 1.08 + (0.07 * ratio)
        return {"tier": "key", "label": "Key", "boost": round(boost, 3)}

    else:
        return {"tier": "base", "label": "Base", "boost": 1.00}


def assign_all_attack_tiers(player_scores):
    """Compute percentile cutoffs and assign tiers to all players."""
    scores = player_scores["total_weighted_goals"]

    elite_cutoff = np.percentile(scores, CONFIG["ELITE_PERCENTILE"])
    star_cutoff = np.percentile(scores, CONFIG["STAR_PERCENTILE"])
    key_cutoff = np.percentile(scores, CONFIG["KEY_PERCENTILE"])

    print(f"[INFO] Attack cutoffs -- Elite: {elite_cutoff:.2f} | Star: {star_cutoff:.2f} | Key: {key_cutoff:.2f}")

    tiers = player_scores["total_weighted_goals"].apply(
        lambda s: assign_attack_tier(s, elite_cutoff, star_cutoff, key_cutoff)
    )

    player_scores["tier"] = tiers.apply(lambda t: t["tier"])
    player_scores["tier_label"] = tiers.apply(lambda t: t["label"])
    player_scores["attack_boost"] = tiers.apply(lambda t: t["boost"])

    return player_scores


# === AUTO DEFENSE SCORING ===

def compute_defense_scores(results):
    """
    Compute goals-conceded-per-match for each team from recent results.
    Lower conceded = better defense = higher boost.
    Returns {team: defense_boost} dict.
    """
    now = datetime.now()
    cutoff = now - pd.DateOffset(years=CONFIG["RECENT_YEARS"])

    df = results.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"] >= cutoff].dropna(subset=["date"])

    if df.empty:
        print("[WARN] No recent results for defense calculation.")
        return {}

    # Home team conceded = away_score, Away team conceded = home_score
    home = df.groupby("home_team").agg(
        matches=("home_score", "count"),
        conceded=("away_score", "sum"),
    ).reset_index().rename(columns={"home_team": "team"})

    away = df.groupby("away_team").agg(
        matches=("away_score", "count"),
        conceded=("home_score", "sum"),
    ).reset_index().rename(columns={"away_team": "team"})

    combined = pd.concat([home, away]).groupby("team").sum().reset_index()
    combined = combined[combined["matches"] >= CONFIG["MIN_MATCHES_DEFENSE"]]
    combined["goals_conceded_per_match"] = combined["conceded"] / combined["matches"]

    # Scale: best defense -> 1.12, worst -> 1.03
    gc = combined["goals_conceded_per_match"]
    if gc.max() == gc.min():
        combined["defense_boost"] = CONFIG["DEF_BOOST_MIN"]
    else:
        # Invert: lower conceded = higher boost
        normalized = 1 - (gc - gc.min()) / (gc.max() - gc.min())
        combined["defense_boost"] = (
            CONFIG["DEF_BOOST_MIN"] + normalized * (CONFIG["DEF_BOOST_MAX"] - CONFIG["DEF_BOOST_MIN"])
        ).round(3)

    print(f"[INFO] Computed defense scores for {len(combined)} teams")

    return dict(zip(combined["team"], combined["defense_boost"]))


# === WC 2026 DEFENSIVE PLAYER OVERRIDES ===
# Named GK + CB for all 48 World Cup 2026 teams
# Update rosters as squads are confirmed

WC2026_DEFENSIVE_OVERRIDES = {
    # CONCACAF
    "United States": [{"name": "Matt Turner", "position": "GK"}, {"name": "Chris Richards", "position": "CB"}],
    "Mexico": [{"name": "Guillermo Ochoa", "position": "GK"}, {"name": "Cesar Montes", "position": "CB"}],
    "Canada": [{"name": "Milan Borjan", "position": "GK"}, {"name": "Alphonso Davies", "position": "CB"}],
    "Costa Rica": [{"name": "Keylor Navas", "position": "GK"}, {"name": "Francisco Calvo", "position": "CB"}],
    "Jamaica": [{"name": "Andre Blake", "position": "GK"}, {"name": "Damion Lowe", "position": "CB"}],
    "Honduras": [{"name": "Luis Lopez", "position": "GK"}, {"name": "Maynor Figueroa", "position": "CB"}],
    "Panama": [{"name": "Luis Mejia", "position": "GK"}, {"name": "Fidel Escobar", "position": "CB"}],
    "El Salvador": [{"name": "Mario Gonzalez", "position": "GK"}, {"name": "Eriq Zavaleta", "position": "CB"}],
    "Trinidad and Tobago": [{"name": "Marvin Phillip", "position": "GK"}, {"name": "Sheldon Bateau", "position": "CB"}],
    # UEFA
    "France": [{"name": "Mike Maignan", "position": "GK"}, {"name": "William Saliba", "position": "CB"}],
    "Spain": [{"name": "Unai Simon", "position": "GK"}, {"name": "Aymeric Laporte", "position": "CB"}],
    "England": [{"name": "Jordan Pickford", "position": "GK"}, {"name": "John Stones", "position": "CB"}],
    "Germany": [{"name": "Marc-Andre ter Stegen", "position": "GK"}, {"name": "Antonio Rudiger", "position": "CB"}],
    "Portugal": [{"name": "Diogo Costa", "position": "GK"}, {"name": "Ruben Dias", "position": "CB"}],
    "Netherlands": [{"name": "Bart Verbruggen", "position": "GK"}, {"name": "Virgil van Dijk", "position": "CB"}],
    "Italy": [{"name": "Gianluigi Donnarumma", "position": "GK"}, {"name": "Alessandro Bastoni", "position": "CB"}],
    "Belgium": [{"name": "Thibaut Courtois", "position": "GK"}, {"name": "Jan Vertonghen", "position": "CB"}],
    "Croatia": [{"name": "Dominik Livakovic", "position": "GK"}, {"name": "Josko Gvardiol", "position": "CB"}],
    "Denmark": [{"name": "Kasper Schmeichel", "position": "GK"}, {"name": "Andreas Christensen", "position": "CB"}],
    "Switzerland": [{"name": "Yann Sommer", "position": "GK"}, {"name": "Manuel Akanji", "position": "CB"}],
    "Austria": [{"name": "Patrick Pentz", "position": "GK"}, {"name": "David Alaba", "position": "CB"}],
    "Serbia": [{"name": "Predrag Rajkovic", "position": "GK"}, {"name": "Nikola Milenkovic", "position": "CB"}],
    "Poland": [{"name": "Wojciech Szczesny", "position": "GK"}, {"name": "Jan Bednarek", "position": "CB"}],
    "Ukraine": [{"name": "Anatoliy Trubin", "position": "GK"}, {"name": "Illia Zabarnyi", "position": "CB"}],
    "Turkey": [{"name": "Altay Bayindir", "position": "GK"}, {"name": "Merih Demiral", "position": "CB"}],
    "Scotland": [{"name": "Angus Gunn", "position": "GK"}, {"name": "Grant Hanley", "position": "CB"}],
    "Wales": [{"name": "Danny Ward", "position": "GK"}, {"name": "Ben Davies", "position": "CB"}],
    # CONMEBOL
    "Argentina": [{"name": "Emiliano Martinez", "position": "GK"}, {"name": "Cristian Romero", "position": "CB"}],
    "Brazil": [{"name": "Alisson", "position": "GK"}, {"name": "Marquinhos", "position": "CB"}],
    "Uruguay": [{"name": "Sergio Rochet", "position": "GK"}, {"name": "Jose Maria Gimenez", "position": "CB"}],
    "Colombia": [{"name": "David Ospina", "position": "GK"}, {"name": "Davinson Sanchez", "position": "CB"}],
    "Ecuador": [{"name": "Hernan Galindez", "position": "GK"}, {"name": "Piero Hincapie", "position": "CB"}],
    "Chile": [{"name": "Claudio Bravo", "position": "GK"}, {"name": "Gary Medel", "position": "CB"}],
    "Paraguay": [{"name": "Antony Silva", "position": "GK"}, {"name": "Gustavo Gomez", "position": "CB"}],
    "Peru": [{"name": "Pedro Gallese", "position": "GK"}, {"name": "Alexander Callens", "position": "CB"}],
    "Bolivia": [{"name": "Carlos Lampe", "position": "GK"}, {"name": "Jose Sagredo", "position": "CB"}],
    "Venezuela": [{"name": "Rafael Romo", "position": "GK"}, {"name": "Yordan Osorio", "position": "CB"}],
    # AFC
    "Japan": [{"name": "Shuichi Gonda", "position": "GK"}, {"name": "Ko Itakura", "position": "CB"}],
    "South Korea": [{"name": "Kim Seung-gyu", "position": "GK"}, {"name": "Kim Min-jae", "position": "CB"}],
    "Australia": [{"name": "Mathew Ryan", "position": "GK"}, {"name": "Harry Souttar", "position": "CB"}],
    "Saudi Arabia": [{"name": "Mohammed Al-Owais", "position": "GK"}, {"name": "Ali Al-Bulaihi", "position": "CB"}],
    "Iran": [{"name": "Alireza Beiranvand", "position": "GK"}, {"name": "Morteza Pouraliganji", "position": "CB"}],
    "Qatar": [{"name": "Saad Al-Sheeb", "position": "GK"}, {"name": "Bassam Al-Rawi", "position": "CB"}],
    "Iraq": [{"name": "Jalal Hassan", "position": "GK"}, {"name": "Ahmed Ibrahim", "position": "CB"}],
    "Uzbekistan": [{"name": "Eldorbek Suyunov", "position": "GK"}, {"name": "Rustam Ashurmatov", "position": "CB"}],
    # CAF
    "Morocco": [{"name": "Yassine Bounou", "position": "GK"}, {"name": "Nayef Aguerd", "position": "CB"}],
    "Senegal": [{"name": "Edouard Mendy", "position": "GK"}, {"name": "Kalidou Koulibaly", "position": "CB"}],
    "Nigeria": [{"name": "Francis Uzoho", "position": "GK"}, {"name": "William Troost-Ekong", "position": "CB"}],
    "Cameroon": [{"name": "Andre Onana", "position": "GK"}, {"name": "Nicolas Nkoulou", "position": "CB"}],
    "Ghana": [{"name": "Richard Ofori", "position": "GK"}, {"name": "Daniel Amartey", "position": "CB"}],
    "Egypt": [{"name": "Mohamed El-Shenawy", "position": "GK"}, {"name": "Mahmoud Hamdy", "position": "CB"}],
    "Tunisia": [{"name": "Aymen Dahmen", "position": "GK"}, {"name": "Montassar Talbi", "position": "CB"}],
    "Algeria": [{"name": "Rais Mbolhi", "position": "GK"}, {"name": "Aissa Mandi", "position": "CB"}],
    # OFC
    "New Zealand": [{"name": "Stefan Marinovic", "position": "GK"}, {"name": "Winston Reid", "position": "CB"}],
}


# === FINAL ASSEMBLY ===

def build_star_players():
    """
    Main builder: assemble 2 attackers + 2 defenders per team.
    Output: {team: [player_dict, ...]}
    """
    print("=" * 60)
    print("MUNDIALISTA AI -- Star Player Builder v2")
    print("=" * 60)

    # Load data
    goalscorers = pd.read_csv(DATA_DIR / "goalscorers.csv")
    results = pd.read_csv(DATA_DIR / "results.csv")

    print(f"[INFO] Loaded {len(goalscorers)} goals, {len(results)} matches")

    # ATTACK: compute scores and assign tiers
    attack_scores = compute_attack_scores(goalscorers, results)
    if attack_scores.empty:
        print("[ERROR] No attack scores computed. Aborting.")
        return {}

    attack_scores = assign_all_attack_tiers(attack_scores)

    # DEFENSE: compute auto scores
    defense_boosts = compute_defense_scores(results)

    # ASSEMBLE per team
    output = {}
    all_teams = set(attack_scores["team"].unique()) | set(defense_boosts.keys()) | set(WC2026_DEFENSIVE_OVERRIDES.keys())

    for team in sorted(all_teams):
        players = []

        # --- ATTACKERS ---
        team_attackers = attack_scores[attack_scores["team"] == team].sort_values(
            "total_weighted_goals", ascending=False
        ).head(CONFIG["ATTACKERS_PER_TEAM"])

        for _, row in team_attackers.iterrows():
            players.append({
                "name": normalize_name(row["name"]),
                "role": "attacker",
                "tier": row["tier"],
                "tier_label": row["tier_label"],
                "attack_boost": row["attack_boost"],
                "defense_boost": 1.0,
                "goals": int(row["raw_goals"]),
                "weighted_score": round(row["total_weighted_goals"], 2),
            })

        # --- DEFENDERS ---
        team_def_boost = defense_boosts.get(team, CONFIG["DEF_BOOST_MIN"])

        if team in WC2026_DEFENSIVE_OVERRIDES:
            for defender in WC2026_DEFENSIVE_OVERRIDES[team][:CONFIG["DEFENDERS_PER_TEAM"]]:
                players.append({
                    "name": normalize_name(defender["name"]),
                    "role": "defender",
                    "tier": "defender",
                    "tier_label": "Defender",
                    "attack_boost": 1.0,
                    "defense_boost": team_def_boost,
                    "position": defender.get("position", "DEF"),
                })
        else:
            # Auto-generate unnamed defensive entry for non-WC teams
            players.append({
                "name": team + " Defensive Unit",
                "role": "defender",
                "tier": "defender",
                "tier_label": "Defender",
                "attack_boost": 1.0,
                "defense_boost": team_def_boost,
                "position": "DEF",
            })

        # Deduplicate
        players = deduplicate_players(players)

        if players:
            output[team] = players

    return output


# === SAVE & REPORT ===

def save_star_players(output):
    """Save to star_players.json and print summary stats."""
    out_path = DATA_DIR / "star_players.json"

    # Backup old file
    if out_path.exists():
        backup_path = DATA_DIR / "star_players_v1_backup.json"
        shutil.copy2(out_path, backup_path)
        print(f"[INFO] Backed up v1 to {backup_path}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Stats
    total_teams = len(output)
    total_players = sum(len(v) for v in output.values())
    attackers = sum(1 for v in output.values() for p in v if p["role"] == "attacker")
    defenders = sum(1 for v in output.values() for p in v if p["role"] == "defender")

    elites = sum(1 for v in output.values() for p in v if p.get("tier") == "elite")
    stars = sum(1 for v in output.values() for p in v if p.get("tier") == "star")
    keys = sum(1 for v in output.values() for p in v if p.get("tier") == "key")

    print("")
    print("=" * 60)
    print("STAR PLAYERS v2 GENERATED")
    print("=" * 60)
    print(f"   Teams:      {total_teams}")
    print(f"   Players:    {total_players} ({attackers} attackers + {defenders} defenders)")
    print(f"   Elite:      {elites}")
    print(f"   Star:       {stars}")
    print(f"   Key:        {keys}")
    print(f"   Defenders:  {defenders}")
    print(f"   Saved to:   {out_path}")
    print("=" * 60)

    # Show top 10 attackers
    all_attackers = []
    for team, players in output.items():
        for p in players:
            if p["role"] == "attacker":
                all_attackers.append({**p, "team": team})

    all_attackers.sort(key=lambda x: x["attack_boost"], reverse=True)

    print("")
    print("TOP 10 ATTACKERS:")
    for i, p in enumerate(all_attackers[:10], 1):
        print(f"   {i:2d}. {p['name']:<30s} ({p['team']:<20s}) {p['tier_label']:<8s} -> {p['attack_boost']}")

    # Show top 10 defensive teams
    def_teams = []
    for team, players in output.items():
        for p in players:
            if p["role"] == "defender":
                def_teams.append({"team": team, "name": p["name"], "defense_boost": p["defense_boost"]})
                break

    def_teams.sort(key=lambda x: x["defense_boost"], reverse=True)

    print("")
    print("TOP 10 DEFENSIVE TEAMS:")
    for i, d in enumerate(def_teams[:10], 1):
        print(f"   {i:2d}. {d['team']:<25s} -> {d['defense_boost']}")


if __name__ == "__main__":
    output = build_star_players()
    if output:
        save_star_players(output)
    else:
        print("[ERROR] No output generated.")
