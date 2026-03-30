"""
Task 13: Dictionaries and Counter
===================================
"""
from collections import Counter
import numpy as np

# ── PART A: Dictionary deep dive ───────────────────────────────
teams = {
    "Jamaica": {
        "avg_gf": 1.29,
        "avg_ga": 0.71,
        "last_7_gf": [1, 0, 2, 1, 0, 3, 2],
        "last_7_ga": [0, 1, 1, 1, 2, 0, 0],
    },
    "New Caledonia": {
        "avg_gf": 1.14,
        "avg_ga": 1.29,
        "last_7_gf": [1, 0, 2, 1, 0, 1, 3],
        "last_7_ga": [1, 2, 1, 0, 4, 1, 0],
    },
}

print("=== PART A: NESTED DICTIONARIES ===")
print(f"Jamaica avg_gf: {teams['Jamaica']['avg_gf']}")
print(f"New Caledonia last_7_ga: {teams['New Caledonia']['last_7_ga']}")
diff = teams["Jamaica"]["avg_gf"] - teams["New Caledonia"]["avg_gf"]
print(f"Difference in avg_gf: {diff:.2f}")

# ── PART B: Counting scorelines with Counter ───────────────────
rng = np.random.default_rng(42)
home_goals = rng.poisson(1.3, size=1000)
away_goals = rng.poisson(0.8, size=1000)

scorelines = list(zip(home_goals, away_goals))
counts = Counter(scorelines)

print("\n=== TOP 10 SCORELINES ===")
for (h, a), count in counts.most_common(10):
    pct = count / 1000 * 100
    print(f"  {h}-{a}: {count} times ({pct:.1f}%)")

# ── PART C: Computing match outcomes from Counter ───────────────
home_wins = sum(c for (h, a), c in counts.items() if h > a)
draws = sum(c for (h, a), c in counts.items() if h == a)
away_wins = sum(c for (h, a), c in counts.items() if h < a)

total = home_wins + draws + away_wins
print(f"\nHome Win: {home_wins/total*100:.1f}%")
print(f"Draw: {draws/total*100:.1f}%")
print(f"Away Win: {away_wins/total*100:.1f}%")

# ── PART D: Building the analytics dict ─────────────────────────
analytics = {
    "home_win_pct": home_wins / total * 100,
    "draw_pct": draws / total * 100,
    "away_win_pct": away_wins / total * 100,
    "top5_scorelines": counts.most_common(5),
    "home_exp": home_goals.mean(),
    "away_exp": away_goals.mean(),
    "n": total,
}

print("\n=== ANALYTICS ===")
for key, value in analytics.items():
    print(f"  {key}: {value}")

# ── PART E: The .items(), .keys(), .values() methods ───────────
print("\n=== DICTIONARY METHODS ===")
print(f"Keys: {list(analytics.keys())}")
print(f"Values: {list(analytics.values())}")
print("\nFormatted items:")
for key, value in analytics.items():
    print(f"  {key}: {value}")