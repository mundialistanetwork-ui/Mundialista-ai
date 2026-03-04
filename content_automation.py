"""
Mundialista Network - Content Automation Tools v2
Uses REAL match data from 258+ teams.
Includes WC 2026 group stage predictions!
"""
import numpy as np
import pandas as pd
from collections import Counter
from datetime import datetime
import os, sys

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RESULTS_CSV = os.path.join(DATA_DIR, "results.csv")

def load_real_data(years_lookback=4):
    if not os.path.exists(RESULTS_CSV):
        print("ERROR: results.csv not found!"); sys.exit(1)
    df = pd.read_csv(RESULTS_CSV)
    df["date"] = pd.to_datetime(df["date"])
    cutoff = df["date"].max() - pd.DateOffset(years=years_lookback)
    return df[df["date"] >= cutoff].copy()

def get_team_stats(results, team, last_n=40):
    home = results[results["home_team"] == team].tail(last_n)
    away = results[results["away_team"] == team].tail(last_n)
    gf = list(home["home_score"].values) + list(away["away_score"].values)
    ga = list(home["away_score"].values) + list(away["home_score"].values)
    if len(gf) == 0:
        return None
    gf = np.array(gf[-last_n:])
    ga = np.array(ga[-last_n:])
    return {"avg_gf": float(np.mean(gf)), "avg_ga": float(np.mean(ga)),
            "std_gf": float(max(np.std(gf), 0.3)), "std_ga": float(max(np.std(ga), 0.3)),
            "n_matches": len(gf), "goals_for": gf, "goals_against": ga}

print("Loading match data...")
RESULTS_DF = load_real_data()
ALL_TEAMS = sorted(set(RESULTS_DF["home_team"].unique()) | set(RESULTS_DF["away_team"].unique()))
print(f"Loaded {len(RESULTS_DF):,} matches, {len(ALL_TEAMS)} teams")

_all_gf = []
_all_ga = []
for _t in ALL_TEAMS:
    _s = get_team_stats(RESULTS_DF, _t)
    if _s and _s["n_matches"] >= 3:
        _all_gf.append(_s["avg_gf"])
        _all_ga.append(_s["avg_ga"])
GLOBAL_GF = float(np.median(_all_gf)) if _all_gf else 1.2
GLOBAL_GA = float(np.median(_all_ga)) if _all_ga else 1.2
print(f"Global baseline: {GLOBAL_GF:.2f} GF / {GLOBAL_GA:.2f} GA")

# Opponent-strength ratings
from strength_adjust import compute_team_ratings, get_adjusted_stats
print("Computing opponent-strength ratings...")
TEAM_RATINGS = compute_team_ratings(RESULTS_DF)
print(f"Ratings computed for {len(TEAM_RATINGS)} teams")


# Opponent-strength ratings
from strength_adjust import compute_team_ratings, get_adjusted_stats
print("Computing opponent-strength ratings...")
TEAM_RATINGS = compute_team_ratings(RESULTS_DF)
print(f"Ratings computed for {len(TEAM_RATINGS)} teams")


WC2026_GROUPS = {
    "A": ["United States", "Morocco", "Scotland", "Kenya"],
    "B": ["Portugal", "Ecuador", "Saudi Arabia", "Indonesia"],
    "C": ["Mexico", "Japan", "Venezuela", "Uzbekistan"],
    "D": ["France", "Colombia", "Costa Rica", "Bahrain"],
    "E": ["Brazil", "Serbia", "Iran", "Egypt"],
    "F": ["Germany", "Uruguay", "South Korea", "DR Congo"],
    "G": ["Argentina", "Australia", "Ghana", "Trinidad and Tobago"],
    "H": ["England", "Senegal", "Denmark", "Panama"],
    "I": ["Spain", "Nigeria", "Peru", "New Zealand"],
    "J": ["Netherlands", "Canada", "Cameroon", "Jamaica"],
    "K": ["Italy", "Switzerland", "Tunisia", "Honduras"],
    "L": ["Croatia", "Chile", "Algeria", "Bolivia"],
}

def quick_simulate(home_team, away_team, n_sims=10200):
    home_stats = get_team_stats(RESULTS_DF, home_team)
    away_stats = get_team_stats(RESULTS_DF, away_team)
    if home_stats is None:
        home_stats = {"avg_gf": GLOBAL_GF, "avg_ga": GLOBAL_GA, "n_matches": 1}
    if away_stats is None:
        away_stats = {"avg_gf": GLOBAL_GF, "avg_ga": GLOBAL_GA, "n_matches": 1}
    # Opponent-strength adjustment
    h_adj = get_adjusted_stats(RESULTS_DF, home_team, TEAM_RATINGS)
    a_adj = get_adjusted_stats(RESULTS_DF, away_team, TEAM_RATINGS)
    if h_adj is not None:
        home_stats["avg_gf"] = h_adj["blended_gf"]
        home_stats["avg_ga"] = h_adj["blended_ga"]
    if a_adj is not None:
        away_stats["avg_gf"] = a_adj["blended_gf"]
        away_stats["avg_ga"] = a_adj["blended_ga"]
    # Shrinkage toward global mean
    shrink_k = 8
    h_n = home_stats["n_matches"]
    a_n = away_stats["n_matches"]
    h_gf = (h_n * home_stats["avg_gf"] + shrink_k * GLOBAL_GF) / (h_n + shrink_k)
    h_ga = (h_n * home_stats["avg_ga"] + shrink_k * GLOBAL_GA) / (h_n + shrink_k)
    a_gf = (a_n * away_stats["avg_gf"] + shrink_k * GLOBAL_GF) / (a_n + shrink_k)
    a_ga = (a_n * away_stats["avg_ga"] + shrink_k * GLOBAL_GA) / (a_n + shrink_k)
    home_lambda = max(0.3, h_gf * (a_ga / GLOBAL_GA) * 1.05)
    away_lambda = max(0.3, a_gf * (h_ga / GLOBAL_GA) * 0.95)
    rng = np.random.default_rng(42)
    home_goals = rng.poisson(home_lambda, n_sims)
    away_goals = rng.poisson(away_lambda, n_sims)
    home_wins = int(np.sum(home_goals > away_goals))
    draws = int(np.sum(home_goals == away_goals))
    away_wins = int(np.sum(home_goals < away_goals))
    scorelines = list(zip(home_goals.tolist(), away_goals.tolist()))
    score_counts = Counter(scorelines)
    top5 = score_counts.most_common(5)
    if home_lambda >= away_lambda:
        favourite, underdog = home_team, away_team
        upset_prob = away_wins / n_sims * 100
    else:
        favourite, underdog = away_team, home_team
        upset_prob = home_wins / n_sims * 100
    return {"home_win_pct": home_wins / n_sims * 100,
            "draw_pct": draws / n_sims * 100,
            "away_win_pct": away_wins / n_sims * 100,
            "home_exp": float(np.mean(home_goals)),
            "away_exp": float(np.mean(away_goals)),
            "home_lambda": home_lambda,
            "away_lambda": away_lambda,
            "top5_scorelines": top5,
            "upset_prob": upset_prob,
            "favourite": favourite,
            "underdog": underdog,
            "n": n_sims,
            "home_n_matches": home_stats["n_matches"],
            "away_n_matches": away_stats["n_matches"]}
def generate_match_preview(home_team, away_team, a):
    hw, dr, aw = a["home_win_pct"], a["draw_pct"], a["away_win_pct"]
    hx, ax = a["home_exp"], a["away_exp"]
    ts = a["top5_scorelines"][0]
    n = a["n"]
    hn, an = a["home_n_matches"], a["away_n_matches"]
    up = a["upset_prob"]
    lines = [
        f"MATCH PREDICTION | {home_team} vs {away_team}",
        f"Powered by Mundialista Network AI | {n:,} Simulations",
        f"Based on {hn} + {an} real matches",
        "",
        "WIN PROBABILITIES:",
        f"  {home_team}: {hw:.1f}%",
        f"  Draw: {dr:.1f}%",
        f"  {away_team}: {aw:.1f}%",
        "",
        "EXPECTED GOALS:",
        f"  {home_team}: {hx:.2f} xG",
        f"  {away_team}: {ax:.2f} xG",
        "",
        f"MOST LIKELY SCORE: {home_team} {ts[0][0]} - {ts[0][1]} {away_team} ({ts[1]/n*100:.1f}%)",
        f"UPSET PROBABILITY: {up:.1f}%",
        "",
        "#WorldCup2026 #WC2026 #MundialistaNetwork #NuestraIA",
    ]
    return "\n".join(lines)

def generate_spanish_preview(home_team, away_team, a):
    hw, dr, aw = a["home_win_pct"], a["draw_pct"], a["away_win_pct"]
    hx, ax = a["home_exp"], a["away_exp"]
    ts = a["top5_scorelines"][0]
    n = a["n"]
    hn, an = a["home_n_matches"], a["away_n_matches"]
    up = a["upset_prob"]
    lines = [
        f"PREDICCION | {home_team} vs {away_team}",
        f"Mundialista Network AI | {n:,} Simulaciones",
        f"Basado en {hn} + {an} partidos reales",
        "",
        "PROBABILIDADES:",
        f"  {home_team}: {hw:.1f}%",
        f"  Empate: {dr:.1f}%",
        f"  {away_team}: {aw:.1f}%",
        "",
        "GOLES ESPERADOS:",
        f"  {home_team}: {hx:.2f} xG",
        f"  {away_team}: {ax:.2f} xG",
        "",
        f"MARCADOR MAS PROBABLE: {home_team} {ts[0][0]} - {ts[0][1]} {away_team} ({ts[1]/n*100:.1f}%)",
        f"PROBABILIDAD DE SORPRESA: {up:.1f}%",
        "",
        "#Mundial2026 #WC2026 #MundialistaNetwork #NuestraIA",
    ]
    return "\n".join(lines)

def generate_twitter_thread(home_team, away_team, a):
    hw, dr, aw = a["home_win_pct"], a["draw_pct"], a["away_win_pct"]
    hx, ax = a["home_exp"], a["away_exp"]
    up = a["upset_prob"]
    fav, dog = a["favourite"], a["underdog"]
    n = a["n"]
    hn, an = a["home_n_matches"], a["away_n_matches"]
    thread = []
    thread.append(f"THREAD: {home_team} vs {away_team} -- AI PREDICTION | Analyzed {hn}+{an} matches, {n:,} sims | #WorldCup2026")
    if hw > aw and hw > dr:
        winner = home_team
    elif aw > hw and aw > dr:
        winner = away_team
    else:
        winner = "DRAW"
    thread.append(f"Our AI favors: {winner} | {home_team}: {hw:.1f}% | Draw: {dr:.1f}% | {away_team}: {aw:.1f}%")
    scores = ""
    for (h, a_sc), cnt in a["top5_scorelines"][:3]:
        scores += f" {home_team} {h}-{a_sc} {away_team}: {cnt/n*100:.1f}%"
    thread.append(f"Top scores:{scores} | xG: {home_team} {hx:.2f} - {ax:.2f} {away_team}")
    alert = "HIGH" if up > 30 else "MODERATE" if up > 20 else "LOW"
    thread.append(f"Upset watch: {alert} | {dog} has {up:.1f}% chance vs {fav}")
    thread.append(f"Try our AI: https://mundialista-ai-8sya4tqzo7fyi65rqgwonw.streamlit.app | #WC2026")
    return thread

def generate_underdog_alert(home_team, away_team, a):
    up = a["upset_prob"]
    dog, fav = a["underdog"], a["favourite"]
    if up < 25:
        return None
    level = "MAXIMUM" if up > 40 else "HIGH" if up > 30 else "MODERATE"
    return f"{level} ALERT: {dog} has {up:.1f}% chance of upsetting {fav}! #WorldCup2026 #WC2026"

def predict_wc2026_group(group_letter):
    if group_letter not in WC2026_GROUPS:
        print(f"Group {group_letter} not found!")
        return
    teams = WC2026_GROUPS[group_letter]
    sep = "=" * 60
    print(sep)
    print(f"WORLD CUP 2026 -- GROUP {group_letter}")
    print(sep)
    print(f"Teams: {', '.join(teams)}")
    print()
    points = {t: 0.0 for t in teams}
    gd = {t: 0.0 for t in teams}
    gf_tot = {t: 0.0 for t in teams}
    num = 0
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            num += 1
            h, aw = teams[i], teams[j]
            r = quick_simulate(h, aw)
            print(f"Match {num}: {h} vs {aw}")
            print(f"  {h} {r['home_win_pct']:.1f}% | Draw {r['draw_pct']:.1f}% | {aw} {r['away_win_pct']:.1f}%")
            print(f"  xG: {h} {r['home_exp']:.2f} - {r['away_exp']:.2f} {aw}")
            print()
            points[h] += r["home_win_pct"] / 100 * 3 + r["draw_pct"] / 100 * 1
            points[aw] += r["away_win_pct"] / 100 * 3 + r["draw_pct"] / 100 * 1
            gd[h] += r["home_exp"] - r["away_exp"]
            gd[aw] += r["away_exp"] - r["home_exp"]
            gf_tot[h] += r["home_exp"]
            gf_tot[aw] += r["away_exp"]
    standings = sorted(teams, key=lambda t: (points[t], gd[t], gf_tot[t]), reverse=True)
    print("-" * 60)
    print(f"PREDICTED GROUP {group_letter} STANDINGS:")
    print("-" * 60)
    header = f"  {'Team':<25s} {'Pts':>6s} {'GD':>7s} {'GF':>6s}"
    print(header)
    print("  " + "-" * 45)
    for rank, t in enumerate(standings, 1):
        tag = "Q" if rank <= 2 else "?" if rank == 3 else "X"
        print(f"  [{tag}] {t:<23s} {points[t]:>5.1f}  {gd[t]:>+6.2f}  {gf_tot[t]:>5.2f}")
    print()
    print("  Q = Qualifies  ? = Possible 3rd place  X = Eliminated")
    return standings

def predict_all_wc2026_groups():
    print()
    print("WORLD CUP 2026 -- FULL GROUP STAGE PREDICTIONS")
    print(f"Powered by Mundialista Network AI")
    print(f"Based on {len(RESULTS_DF):,} real matches from {len(ALL_TEAMS)} teams")
    print()
    all_standings = {}
    for group in sorted(WC2026_GROUPS.keys()):
        standings = predict_wc2026_group(group)
        all_standings[group] = standings
    print()
    print("=" * 60)
    print("PREDICTED QUALIFIERS FROM GROUP STAGE:")
    print("=" * 60)
    for group in sorted(all_standings.keys()):
        s = all_standings[group]
        print(f"  Group {group}: {s[0]}, {s[1]} | 3rd: {s[2]}")
    return all_standings

def show_teams():
    print(f"\nAVAILABLE TEAMS ({len(ALL_TEAMS)} total):")
    print("=" * 70)
    for i, team in enumerate(ALL_TEAMS, 1):
        stats = get_team_stats(RESULTS_DF, team)
        if stats:
            n = stats["n_matches"]
            gf = stats["avg_gf"]
            ga = stats["avg_ga"]
            diff = gf - ga
            print(f"  {i:3d}. {team:<35s} {n:>2d}m  GF:{gf:.1f} GA:{ga:.1f} ({diff:+.1f})")
        else:
            print(f"  {i:3d}. {team:<35s}  (no data)")
    print("=" * 70)

def select_team(prompt):
    while True:
        choice = input(prompt).strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(ALL_TEAMS):
                return ALL_TEAMS[idx]
            else:
                print(f"  Enter a number between 1 and {len(ALL_TEAMS)}")
                continue
        except ValueError:
            pass
        matches = [t for t in ALL_TEAMS if choice.lower() in t.lower()]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print("  Multiple matches:")
            for m in matches:
                print(f"    - {m}")
            print("  Be more specific.")
        else:
            print(f"  Team '{choice}' not found. Try again.")

def interactive_menu():
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  MUNDIALISTA NETWORK -- CONTENT GENERATOR v2")
    print(f"  {len(ALL_TEAMS)} Teams | {len(RESULTS_DF):,} Real Matches")
    print(sep)
    while True:
        print("\nMENU:")
        print("  1. Generate Match Preview (English)")
        print("  2. Generate Match Preview (Spanish)")
        print("  3. Generate Twitter/X Thread")
        print("  4. Check Underdog Alert")
        print("  5. Show All Teams")
        print("  6. Predict WC 2026 Group")
        print("  7. Predict ALL WC 2026 Groups")
        print("  8. Quick Head-to-Head")
        print("  9. Exit")
        choice = input("\nSelect option (1-9): ").strip()
        if choice == "9":
            print("\nHasta la vista! Follow @MundialistaNet")
            break
        if choice == "5":
            show_teams()
            continue
        if choice == "6":
            grp = input("Enter group letter (A-L): ").strip().upper()
            predict_wc2026_group(grp)
            continue
        if choice == "7":
            predict_all_wc2026_groups()
            continue
        if choice == "8":
            home = select_team("\nHome team: ")
            away = select_team("Away team: ")
            print(f"\nSimulating {home} vs {away}...")
            a = quick_simulate(home, away)
            print(f"\n  {home} {a['home_win_pct']:.1f}% | Draw {a['draw_pct']:.1f}% | {away} {a['away_win_pct']:.1f}%")
            print(f"  xG: {home} {a['home_exp']:.2f} - {a['away_exp']:.2f} {away}")
            top = a["top5_scorelines"][0]
            print(f"  Most likely: {home} {top[0][0]}-{top[0][1]} {away} ({top[1]/a['n']*100:.1f}%)")
            continue
        if choice in ["1", "2", "3", "4"]:
            home = select_team("\nHome team (name or number): ")
            away = select_team("Away team (name or number): ")
            print(f"\nRunning 10,200 simulations: {home} vs {away}...")
            analytics = quick_simulate(home, away)
            if choice == "1":
                print("\n" + sep)
                print("ENGLISH PREVIEW:")
                print(sep)
                print(generate_match_preview(home, away, analytics))
            elif choice == "2":
                print("\n" + sep)
                print("SPANISH PREVIEW:")
                print(sep)
                print(generate_spanish_preview(home, away, analytics))
            elif choice == "3":
                print("\n" + sep)
                print("TWITTER THREAD:")
                print(sep)
                thread = generate_twitter_thread(home, away, analytics)
                for i, tweet in enumerate(thread, 1):
                    print(f"\n{'-' * 40}")
                    print(f"Tweet {i}/{len(thread)}:")
                    print(f"{'-' * 40}")
                    print(tweet)
            elif choice == "4":
                alert = generate_underdog_alert(home, away, analytics)
                print("\n" + sep)
                if alert:
                    print("UNDERDOG ALERT:")
                    print(sep)
                    print(alert)
                else:
                    fav = analytics["favourite"]
                    up = analytics["upset_prob"]
                    print(f"No upset alert -- {fav} is a clear favorite ({up:.1f}% upset chance)")
                    print(sep)
            print("\nContent generated! Copy the text above for your post.")
        else:
            print("Invalid option. Enter 1-9.")

if __name__ == "__main__":
    interactive_menu()