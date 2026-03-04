from data_loader import load_results
import numpy as np
import sys

results = load_results()
all_teams = sorted(set(results['home_team'].unique()) | set(results['away_team'].unique()))

if len(sys.argv) > 1:
    search = " ".join(sys.argv[1:])
else:
    search = input("Enter team name: ").strip()

# Fuzzy match
matches = [t for t in all_teams if search.lower() in t.lower()]

if len(matches) == 0:
    print(f"No team found matching '{search}'")
    print("Try one of these:")
    for t in all_teams:
        print(f"  {t}")
    sys.exit(1)
elif len(matches) > 1:
    print(f"Multiple matches for '{search}':")
    for m in matches:
        print(f"  - {m}")
    team = matches[0]
    print(f"Using: {team}")
else:
    team = matches[0]

# Get all matches
home_matches = results[results['home_team'] == team].copy()
away_matches = results[results['away_team'] == team].copy()

# Build unified match list
all_matches = []
for _, r in home_matches.iterrows():
    all_matches.append({
        "date": r["date"],
        "opponent": r["away_team"],
        "gf": int(r["home_score"]),
        "ga": int(r["away_score"]),
        "venue": "Home",
        "tournament": r["tournament"],
    })
for _, r in away_matches.iterrows():
    all_matches.append({
        "date": r["date"],
        "opponent": r["home_team"],
        "gf": int(r["away_score"]),
        "ga": int(r["home_score"]),
        "venue": "Away",
        "tournament": r["tournament"],
    })

all_matches.sort(key=lambda x: str(x["date"]))

total = len(all_matches)
gf_all = [m["gf"] for m in all_matches]
ga_all = [m["ga"] for m in all_matches]
wins = sum(1 for m in all_matches if m["gf"] > m["ga"])
draws = sum(1 for m in all_matches if m["gf"] == m["ga"])
losses = sum(1 for m in all_matches if m["gf"] < m["ga"])

print()
print("=" * 70)
print(f"  {team} — FULL PROFILE")
print("=" * 70)
print(f"  Total matches (last 4 years): {total}")
print(f"  Record: {wins}W {draws}D {losses}L")
print(f"  Win rate: {wins/total*100:.1f}%")
print(f"  Avg Goals For: {np.mean(gf_all):.2f}")
print(f"  Avg Goals Against: {np.mean(ga_all):.2f}")
print(f"  Avg Goal Diff: {np.mean(gf_all) - np.mean(ga_all):+.2f}")
print(f"  Total Goals Scored: {sum(gf_all)}")
print(f"  Total Goals Conceded: {sum(ga_all)}")
print()

# Opponent breakdown
opponents = {}
for m in all_matches:
    opp = m["opponent"]
    if opp not in opponents:
        opponents[opp] = {"w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "n": 0}
    opponents[opp]["n"] += 1
    opponents[opp]["gf"] += m["gf"]
    opponents[opp]["ga"] += m["ga"]
    if m["gf"] > m["ga"]:
        opponents[opp]["w"] += 1
    elif m["gf"] == m["ga"]:
        opponents[opp]["d"] += 1
    else:
        opponents[opp]["l"] += 1

print(f"OPPONENTS FACED ({len(opponents)} different teams):")
print("-" * 70)
print(f"  {'Opponent':<30s} {'P':>3s} {'W':>3s} {'D':>3s} {'L':>3s} {'GF':>4s} {'GA':>4s} {'GD':>5s}")
print("  " + "-" * 60)
for opp in sorted(opponents.keys(), key=lambda x: opponents[x]["n"], reverse=True):
    o = opponents[opp]
    gd = o["gf"] - o["ga"]
    print(f"  {opp:<30s} {o['n']:>3d} {o['w']:>3d} {o['d']:>3d} {o['l']:>3d} {o['gf']:>4d} {o['ga']:>4d} {gd:>+5d}")

# Tournament breakdown
tournaments = {}
for m in all_matches:
    t = m["tournament"]
    if t not in tournaments:
        tournaments[t] = 0
    tournaments[t] += 1

print()
print("TOURNAMENTS:")
print("-" * 50)
for t in sorted(tournaments.keys(), key=lambda x: tournaments[x], reverse=True):
    print(f"  {t:<40s} {tournaments[t]:>3d} matches")

# Last 15 matches
print()
print("LAST 15 MATCHES:")
print("-" * 70)
for m in all_matches[-15:]:
    if m["gf"] > m["ga"]:
        result = "W"
    elif m["gf"] == m["ga"]:
        result = "D"
    else:
        result = "L"
    print(f"  {str(m['date'])[:10]}  {result}  {team} {m['gf']}-{m['ga']} {m['opponent']:<25s} ({m['venue']}) {m['tournament']}")

print()
print("=" * 70)