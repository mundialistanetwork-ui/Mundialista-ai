"""
Mundialista AI — Content Automation v3
Generates social media content, match previews, and WC 2026 group predictions.

KEY CHANGE: Uses prediction_engine.py as the SINGLE source of truth.
No more duplicate models giving different numbers.
"""

import os
import sys
import json
import math
from datetime import datetime
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

# ── Use the ONE prediction engine ──
from prediction_engine import (
    predict,
    get_all_teams,
    get_team_ranking,
    get_team_points,
    get_team_star_impact,
    _data,
)


# ──────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────

N_SIMS = 10_000
OUTPUT_DIR = Path("content_output")


# ──────────────────────────────────────────────
#  TEAM NAME MAPPING (data ↔ official names)
# ──────────────────────────────────────────────

# Maps WC 2026 official names → names in results.csv
TEAM_NAME_MAP = {
    "Czechia":              "Czech Republic",
    "Türkiye":              "Turkey",
    "Ivory Coast":          "Côte d'Ivoire",
    "Bosnia-Herzegovina":   "Bosnia and Herzegovina",
    "South Korea":          "Korea Republic",
    "DR Congo":             "Congo DR",
    "Cape Verde":           "Cabo Verde",
    "USA":                  "United States",
    "Curaçao":              "Curaçao",  # Check if this exists in your data
}

# Reverse map for display
DISPLAY_NAME_MAP = {v: k for k, v in TEAM_NAME_MAP.items()}


def resolve_team_name(name: str) -> str:
    """Convert display/official name to dataset name."""
    return TEAM_NAME_MAP.get(name, name)


def display_name(name: str) -> str:
    """Convert dataset name to display name."""
    return DISPLAY_NAME_MAP.get(name, name)


def validate_team(name: str) -> bool:
    """Check if team exists in the dataset."""
    resolved = resolve_team_name(name)
    all_teams = get_all_teams()
    return resolved in all_teams


# ──────────────────────────────────────────────
#  WORLD CUP 2026 GROUPS (Updated April 2025)
# ──────────────────────────────────────────────

WC2026_GROUPS = {
    "A": ["Mexico", "South Korea", "South Africa", "Czechia"],
    "B": ["Canada", "Switzerland", "Qatar", "Bosnia-Herzegovina"],
    "C": ["Brazil", "Morocco", "Scotland", "Haiti"],
    "D": ["USA", "Paraguay", "Australia", "Türkiye"],
    "E": ["Germany", "Ecuador", "Ivory Coast", "Curaçao"],
    "F": ["Netherlands", "Japan", "Tunisia", "Sweden"],
    "G": ["Belgium", "Iran", "Egypt", "New Zealand"],
    "H": ["Spain", "Uruguay", "Saudi Arabia", "Cape Verde"],
    "I": ["France", "Senegal", "Norway", "Iraq"],
    "J": ["Argentina", "Austria", "Algeria", "Jordan"],
    "K": ["Portugal", "Colombia", "Uzbekistan", "DR Congo"],
    "L": ["England", "Croatia", "Panama", "Ghana"],
}


# ──────────────────────────────────────────────
#  CORE: MATCH ANALYSIS (wraps prediction_engine)
# ──────────────────────────────────────────────

def analyze_match(home_team: str, away_team: str, neutral: bool = True) -> dict:
    """
    Run a full match analysis using the main prediction engine.
    Returns enriched result dict with content-friendly fields.
    """
    # Resolve names
    home_resolved = resolve_team_name(home_team)
    away_resolved = resolve_team_name(away_team)

    # Use the ONE engine
    home_arg = None if neutral else home_resolved
    result = predict(home_resolved, away_resolved, home=home_arg)

    # Determine favourite/underdog
    if result["team_a_win"] >= result["team_b_win"]:
        favourite = home_team
        underdog = away_team
        upset_prob = result["team_b_win"]
    else:
        favourite = away_team
        underdog = home_team
        upset_prob = result["team_a_win"]

    # Simulation stats from the goals arrays
    goals_a = result.get("goals_a", np.array([]))
    goals_b = result.get("goals_b", np.array([]))

    # Top scorelines from engine
    top_scores = result.get("top_scores", [])

    return {
        # Core probabilities (from the ONE engine)
        "home_win_pct": result["team_a_win"],
        "draw_pct": result["draw"],
        "away_win_pct": result["team_b_win"],

        # Expected goals
        "home_exp": result["team_a_lambda"],
        "away_exp": result["team_b_lambda"],
        "home_lambda": result["team_a_lambda"],
        "away_lambda": result["team_b_lambda"],

        # Rankings
        "home_rank": result["team_a_rank"],
        "away_rank": result["team_b_rank"],

        # Stars
        "home_stars": result.get("team_a_stars", []),
        "away_stars": result.get("team_b_stars", []),

        # Match classification
        "match_type": result.get("match_type", "Competitive"),

        # Top scorelines
        "top5_scorelines": top_scores[:5],

        # Upset analysis
        "favourite": favourite,
        "underdog": underdog,
        "upset_prob": upset_prob,

        # Metadata
        "n": result.get("n_simulations", N_SIMS),
        "engine_version": "v7",

        # Display names
        "home_display": home_team,
        "away_display": away_team,

        # Raw result (for advanced use)
        "_raw": result,
    }


# ──────────────────────────────────────────────
#  CONTENT GENERATORS
# ──────────────────────────────────────────────

def generate_match_preview(home: str, away: str, a: dict) -> str:
    """English match preview for social media."""
    hw, dr, aw = a["home_win_pct"], a["draw_pct"], a["away_win_pct"]
    hx, ax = a["home_exp"], a["away_exp"]
    n = a["n"]
    hr, ar = a["home_rank"], a["away_rank"]

    # Most likely score
    if a["top5_scorelines"]:
        ts = a["top5_scorelines"][0]
        score_str = f"{ts[0]}" if isinstance(ts[0], str) else f"{ts[0][0]}-{ts[0][1]}"
        score_pct = ts[1] if isinstance(ts[1], (int, float)) else 0
        if score_pct < 1:
            score_pct *= 100  # Convert from decimal to %
        score_line = f"MOST LIKELY SCORE: {home} {score_str} ({score_pct:.1f}%)"
    else:
        score_line = ""

    lines = [
        f"⚽ MATCH PREDICTION | {home} vs {away}",
        f"🤖 Powered by Mundialista AI | {n:,} Simulations",
        f"📊 FIFA Rankings: #{hr} vs #{ar}",
        "",
        "WIN PROBABILITIES:",
        f"  🏠 {home}: {hw:.1f}%",
        f"  🤝 Draw: {dr:.1f}%",
        f"  ✈️  {away}: {aw:.1f}%",
        "",
        "EXPECTED GOALS:",
        f"  {home}: {hx:.2f} xG",
        f"  {away}: {ax:.2f} xG",
        "",
        score_line,
        "",
        f"🔮 Upset probability: {a['upset_prob']:.1f}% ({a['underdog']})",
        "",
        "#WorldCup2026 #WC2026 #MundialistaAI",
    ]
    return "\n".join(lines)


def generate_spanish_preview(home: str, away: str, a: dict) -> str:
    """Spanish match preview for social media."""
    hw, dr, aw = a["home_win_pct"], a["draw_pct"], a["away_win_pct"]
    hx, ax = a["home_exp"], a["away_exp"]
    n = a["n"]
    hr, ar = a["home_rank"], a["away_rank"]

    if a["top5_scorelines"]:
        ts = a["top5_scorelines"][0]
        score_str = f"{ts[0]}" if isinstance(ts[0], str) else f"{ts[0][0]}-{ts[0][1]}"
        score_pct = ts[1] if isinstance(ts[1], (int, float)) else 0
        if score_pct < 1:
            score_pct *= 100
        score_line = f"MARCADOR MÁS PROBABLE: {home} {score_str} ({score_pct:.1f}%)"
    else:
        score_line = ""

    lines = [
        f"⚽ PREDICCIÓN | {home} vs {away}",
        f"🤖 Mundialista AI | {n:,} Simulaciones",
        f"📊 Rankings FIFA: #{hr} vs #{ar}",
        "",
        "PROBABILIDADES:",
        f"  🏠 {home}: {hw:.1f}%",
        f"  🤝 Empate: {dr:.1f}%",
        f"  ✈️  {away}: {aw:.1f}%",
        "",
        "GOLES ESPERADOS:",
        f"  {home}: {hx:.2f} xG",
        f"  {away}: {ax:.2f} xG",
        "",
        score_line,
        "",
        f"🔮 Probabilidad de sorpresa: {a['upset_prob']:.1f}% ({a['underdog']})",
        "",
        "#Mundial2026 #WC2026 #MundialistaAI #NuestraIA",
    ]
    return "\n".join(lines)


def generate_twitter_thread(home: str, away: str, a: dict) -> list[str]:
    """Generate a Twitter/X thread (list of tweets)."""
    hw, dr, aw = a["home_win_pct"], a["draw_pct"], a["away_win_pct"]
    hx, ax = a["home_exp"], a["away_exp"]
    n = a["n"]
    fav, dog = a["favourite"], a["underdog"]
    up = a["upset_prob"]

    # Determine predicted winner
    if hw > aw and hw > dr:
        winner = home
    elif aw > hw and aw > dr:
        winner = away
    else:
        winner = "DRAW 🤝"

    thread = []

    # Tweet 1: Hook
    thread.append(
        f"🧵 THREAD: {home} vs {away} — AI PREDICTION\n\n"
        f"📊 {n:,} simulations | Dixon-Coles Poisson model\n\n"
        f"Our AI says: {winner}\n\n"
        f"#WorldCup2026 #WC2026"
    )

    # Tweet 2: Probabilities
    thread.append(
        f"📈 Win Probabilities:\n\n"
        f"🏠 {home}: {hw:.1f}%\n"
        f"🤝 Draw: {dr:.1f}%\n"
        f"✈️ {away}: {aw:.1f}%\n\n"
        f"Expected Goals: {hx:.2f} vs {ax:.2f}"
    )

    # Tweet 3: Top scores
    scores_text = ""
    for sc in a["top5_scorelines"][:3]:
        if isinstance(sc, (list, tuple)) and len(sc) >= 2:
            score_str = str(sc[0])
            pct = sc[1]
            if isinstance(pct, (int, float)):
                if pct < 1:
                    pct *= 100
                scores_text += f"\n  {score_str}: {pct:.1f}%"
    if scores_text:
        thread.append(f"🎯 Most likely scorelines:{scores_text}")

    # Tweet 4: Upset watch
    alert = "🔴 HIGH" if up > 30 else "🟡 MODERATE" if up > 20 else "🟢 LOW"
    thread.append(
        f"⚠️ Upset Watch: {alert}\n\n"
        f"{dog} has a {up:.1f}% chance against {fav}\n\n"
        f"Try our AI: mundialista-ai.streamlit.app\n"
        f"#WC2026 #MundialistaAI"
    )

    return thread


def generate_underdog_alert(home: str, away: str, a: dict) -> str | None:
    """Generate an underdog alert if upset probability is notable."""
    up = a["upset_prob"]
    dog, fav = a["underdog"], a["favourite"]

    if up < 20:
        return None

    if up > 40:
        emoji, level = "🚨🔴", "MAXIMUM"
    elif up > 30:
        emoji, level = "⚠️🟡", "HIGH"
    else:
        emoji, level = "👀🟢", "MODERATE"

    return (
        f"{emoji} UPSET ALERT: {level}\n\n"
        f"{dog} has a {up:.1f}% chance of beating {fav}!\n\n"
        f"#WorldCup2026 #WC2026 #MundialistaAI"
    )


# ──────────────────────────────────────────────
#  WORLD CUP 2026 GROUP PREDICTIONS
# ──────────────────────────────────────────────

def predict_wc2026_group(group_letter: str, verbose: bool = True) -> dict:
    """
    Simulate all matches in a WC 2026 group.
    Returns standings with expected points, GD, GF.
    """
    group_letter = group_letter.upper()
    if group_letter not in WC2026_GROUPS:
        print(f"❌ Group {group_letter} not found! Valid: {sorted(WC2026_GROUPS.keys())}")
        return {}

    display_teams = WC2026_GROUPS[group_letter]
    data_teams = [resolve_team_name(t) for t in display_teams]

    # Validate all teams exist
    all_known = get_all_teams()
    for dt, rt in zip(display_teams, data_teams):
        if rt not in all_known:
            print(f"  ⚠️  {dt} (→ {rt}) not found in dataset. Using defaults.")

    sep = "=" * 62

    if verbose:
        print(sep)
        print(f"  ⚽ WORLD CUP 2026 — GROUP {group_letter}")
        print(sep)
        print(f"  Teams: {', '.join(display_teams)}")
        print()

    # Initialize standings
    points = {t: 0.0 for t in display_teams}
    gd = {t: 0.0 for t in display_teams}
    gf_tot = {t: 0.0 for t in display_teams}
    match_results = []

    match_num = 0
    for i in range(len(display_teams)):
        for j in range(i + 1, len(display_teams)):
            match_num += 1
            h_display = display_teams[i]
            a_display = display_teams[j]

            # Analyze using the ONE engine (neutral venue for group stage)
            a = analyze_match(h_display, a_display, neutral=True)

            if verbose:
                print(f"  Match {match_num}: {h_display} vs {a_display}")
                print(f"    {h_display} {a['home_win_pct']:.1f}%"
                      f" | Draw {a['draw_pct']:.1f}%"
                      f" | {a_display} {a['away_win_pct']:.1f}%")
                print(f"    xG: {a['home_exp']:.2f} vs {a['away_exp']:.2f}")
                if a["top5_scorelines"]:
                    ts = a["top5_scorelines"][0]
                    print(f"    Most likely: {ts[0]}")
                print()

            # Expected points calculation
            hw_frac = a["home_win_pct"] / 100
            dr_frac = a["draw_pct"] / 100
            aw_frac = a["away_win_pct"] / 100

            points[h_display] += hw_frac * 3 + dr_frac * 1
            points[a_display] += aw_frac * 3 + dr_frac * 1

            gd[h_display] += a["home_exp"] - a["away_exp"]
            gd[a_display] += a["away_exp"] - a["home_exp"]

            gf_tot[h_display] += a["home_exp"]
            gf_tot[a_display] += a["away_exp"]

            match_results.append({
                "home": h_display,
                "away": a_display,
                "home_win": a["home_win_pct"],
                "draw": a["draw_pct"],
                "away_win": a["away_win_pct"],
                "home_xg": a["home_exp"],
                "away_xg": a["away_exp"],
            })

    # Sort standings
    standings = sorted(
        display_teams,
        key=lambda t: (points[t], gd[t], gf_tot[t]),
        reverse=True,
    )

    if verbose:
        print(f"  {'─' * 56}")
        print(f"  📊 PREDICTED GROUP {group_letter} STANDINGS:")
        print(f"  {'─' * 56}")
        print(f"  {'':>4} {'Team':<22s} {'Pts':>6s} {'GD':>7s} {'GF':>6s}")
        print(f"  {'':>4} {'─'*22} {'─'*6} {'─'*7} {'─'*6}")

        for rank, t in enumerate(standings, 1):
            if rank <= 2:
                tag = "✅"
            elif rank == 3:
                tag = "🔄"
            else:
                tag = "❌"
            print(f"  {tag} {rank}. {t:<22s}"
                  f" {points[t]:>5.1f}"
                  f"  {gd[t]:>+6.2f}"
                  f"  {gf_tot[t]:>5.2f}")

        print()
        print(f"  ✅ = Qualifies  🔄 = Possible 3rd  ❌ = Eliminated")

    return {
        "group": group_letter,
        "standings": standings,
        "points": points,
        "gd": gd,
        "gf": gf_tot,
        "matches": match_results,
    }


def predict_all_wc2026_groups(verbose: bool = True) -> dict:
    """Predict all 12 World Cup 2026 groups."""
    sep = "=" * 62

    if verbose:
        print(f"\n{sep}")
        print(f"  ⚽ WORLD CUP 2026 — FULL GROUP STAGE PREDICTIONS")
        print(f"  🤖 Powered by Mundialista AI (Dixon-Coles Poisson)")
        print(f"  📊 Based on {len(get_all_teams())} teams in database")
        print(f"{sep}\n")

    all_results = {}

    for group in sorted(WC2026_GROUPS.keys()):
        result = predict_wc2026_group(group, verbose=verbose)
        all_results[group] = result
        if verbose:
            print()

    # Summary
    if verbose:
        print(f"\n{sep}")
        print(f"  🏆 PREDICTED QUALIFIERS FROM GROUP STAGE:")
        print(f"{sep}")
        for group in sorted(all_results.keys()):
            s = all_results[group]["standings"]
            print(f"  Group {group}: ✅ {s[0]:<18s} ✅ {s[1]:<18s} 🔄 {s[2]}")

    return all_results


def save_group_predictions(results: dict, path: str = None):
    """Save group predictions to JSON for later use."""
    if path is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = OUTPUT_DIR / f"wc2026_groups_{timestamp}.json"

    # Clean for JSON serialization
    clean = {}
    for group, data in results.items():
        clean[group] = {
            "group": data["group"],
            "standings": data["standings"],
            "points": {k: round(v, 2) for k, v in data["points"].items()},
            "gd": {k: round(v, 3) for k, v in data["gd"].items()},
            "gf": {k: round(v, 3) for k, v in data["gf"].items()},
            "matches": data["matches"],
        }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved to {path}")


# ──────────────────────────────────────────────
#  TEAM BROWSER
# ──────────────────────────────────────────────

def show_teams():
    """Display all available teams with basic stats."""
    all_teams = get_all_teams()
    print(f"\n  📋 AVAILABLE TEAMS ({len(all_teams)} total)")
    print(f"  {'='*60}")

    for i, team in enumerate(all_teams, 1):
        rank = get_team_ranking(team)
        rank_str = f"#{rank:<4d}" if rank < 200 else "  —  "
        print(f"  {i:>4d}. {rank_str} {team}")

        # Print 20 per page
        if i % 40 == 0 and i < len(all_teams):
            cont = input(f"\n  Showing {i}/{len(all_teams)}. Press Enter for more (q to stop): ")
            if cont.lower() == 'q':
                break

    print(f"  {'='*60}")


def select_team(prompt: str) -> str:
    """Interactive team selector with fuzzy matching."""
    all_teams = get_all_teams()

    while True:
        choice = input(prompt).strip()

        if not choice:
            continue

        # Try as number
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(all_teams):
                selected = all_teams[idx]
                print(f"  → {selected}")
                return selected
            else:
                print(f"  ❌ Enter a number between 1 and {len(all_teams)}")
                continue
        except ValueError:
            pass

        # Try exact match first
        if choice in all_teams:
            return choice

        # Try name resolution (WC group names)
        resolved = resolve_team_name(choice)
        if resolved in all_teams:
            print(f"  → {resolved}")
            return resolved

        # Fuzzy match
        matches = [t for t in all_teams if choice.lower() in t.lower()]

        if len(matches) == 1:
            print(f"  → {matches[0]}")
            return matches[0]
        elif len(matches) > 1:
            print(f"  Multiple matches:")
            for m in matches[:10]:
                print(f"    - {m}")
            if len(matches) > 10:
                print(f"    ... and {len(matches)-10} more")
            print(f"  Be more specific.")
        else:
            print(f"  ❌ '{choice}' not found. Try again.")


# ──────────────────────────────────────────────
#  INTERACTIVE MENU
# ──────────────────────────────────────────────

def interactive_menu():
    sep = "=" * 62

    print(f"\n{sep}")
    print(f"  ⚽ MUNDIALISTA AI — Content Generator v3")
    print(f"  📊 {len(get_all_teams())} Teams | Dixon-Coles Poisson Engine")
    print(f"{sep}")

    while True:
        print(f"\n  {'─'*50}")
        print(f"  📝 CONTENT MENU:")
        print(f"  {'─'*50}")
        print(f"  1. 🇬🇧 Match Preview (English)")
        print(f"  2. 🇪🇸 Match Preview (Español)")
        print(f"  3. 🐦 Twitter/X Thread")
        print(f"  4. 🚨 Underdog Alert Check")
        print(f"  5. ⚡ Quick Head-to-Head")
        print(f"  {'─'*50}")
        print(f"  🏆 WORLD CUP 2026:")
        print(f"  {'─'*50}")
        print(f"  6. 📊 Predict One Group (A-L)")
        print(f"  7. 🌍 Predict ALL Groups")
        print(f"  {'─'*50}")
        print(f"  8. 📋 Show All Teams")
        print(f"  9. 🚪 Exit")
        print(f"  {'─'*50}")

        choice = input("\n  Select (1-9): ").strip()

        if choice == "9":
            print(f"\n  ¡Hasta la vista! Follow @MundialistaAI ⚽")
            break

        elif choice == "8":
            show_teams()

        elif choice == "6":
            grp = input("  Enter group letter (A-L): ").strip().upper()
            result = predict_wc2026_group(grp)
            if result:
                save_q = input("\n  Save results to JSON? (y/n): ").strip().lower()
                if save_q == "y":
                    save_group_predictions({grp: result})

        elif choice == "7":
            results = predict_all_wc2026_groups()
            save_q = input("\n  Save all results to JSON? (y/n): ").strip().lower()
            if save_q == "y":
                save_group_predictions(results)

        elif choice == "5":
            home = select_team("\n  🏠 Home team: ")
            away = select_team("  ✈️  Away team: ")
            neutral_q = input("  Neutral venue? (y/n, default y): ").strip().lower()
            is_neutral = neutral_q != "n"

            print(f"\n  🧠 Analyzing {home} vs {away}...")
            a = analyze_match(home, away, neutral=is_neutral)

            print(f"\n  {sep}")
            print(f"  {home} vs {away}")
            print(f"  {'─'*50}")
            print(f"  🏠 {home}: {a['home_win_pct']:.1f}%"
                  f"  |  🤝 Draw: {a['draw_pct']:.1f}%"
                  f"  |  ✈️  {away}: {a['away_win_pct']:.1f}%")
            print(f"  ⚽ xG: {home} {a['home_exp']:.2f}"
                  f" vs {a['away_exp']:.2f} {away}")
            if a["top5_scorelines"]:
                ts = a["top5_scorelines"][0]
                print(f"  🎯 Most likely: {ts[0]} ({ts[1]:.1f}%)")
            print(f"  {sep}")

        elif choice in ["1", "2", "3", "4"]:
            home = select_team("\n  🏠 Home team (name or number): ")
            away = select_team("  ✈️  Away team: ")

            print(f"\n  🧠 Running prediction: {home} vs {away}...")
            a = analyze_match(home, away)

            if choice == "1":
                print(f"\n{sep}")
                print("  🇬🇧 ENGLISH PREVIEW:")
                print(sep)
                content = generate_match_preview(home, away, a)
                print(content)

            elif choice == "2":
                print(f"\n{sep}")
                print("  🇪🇸 PREVIEW EN ESPAÑOL:")
                print(sep)
                content = generate_spanish_preview(home, away, a)
                print(content)

            elif choice == "3":
                print(f"\n{sep}")
                print("  🐦 TWITTER/X THREAD:")
                print(sep)
                thread = generate_twitter_thread(home, away, a)
                for i, tweet in enumerate(thread, 1):
                    print(f"\n  {'─'*45}")
                    print(f"  Tweet {i}/{len(thread)} ({len(tweet)} chars):")
                    print(f"  {'─'*45}")
                    print(f"  {tweet}")

            elif choice == "4":
                alert = generate_underdog_alert(home, away, a)
                print(f"\n{sep}")
                if alert:
                    print("  🚨 UNDERDOG ALERT:")
                    print(sep)
                    print(f"  {alert}")
                else:
                    print(f"  ✅ No upset alert — {a['favourite']} is a clear"
                          f" favorite ({a['upset_prob']:.1f}% upset chance)")
                print(sep)

            print(f"\n  📋 Content ready! Copy the text above for your post.")

        else:
            print("  ❌ Invalid option. Enter 1-9.")


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    interactive_menu()