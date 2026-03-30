"""
Task 19: Complete Match Simulation Function
============================================
"""
import numpy as np
from typing import Dict
from collections import Counter

TOTAL_MINUTES = 90
HALF_TIME = 45

# Lambda profile from Task 18
_MULTIPLIERS = np.ones(90)
_MULTIPLIERS[0:15] = 0.85
_MULTIPLIERS[15:45] = 1.00
_MULTIPLIERS[45:60] = 1.10
_MULTIPLIERS[60:80] = 1.05
_MULTIPLIERS[80:90] = 1.30
_NORM_FACTOR = _MULTIPLIERS.sum() / 90.0

def lambda_profile(base_rate: float, minute: int) -> float:
    """Return the instantaneous Poisson rate for a single minute."""
    if base_rate <= 0 or minute < 0 or minute >= 90:
        return 0.0
    return (base_rate / 90.0) * _MULTIPLIERS[minute] / _NORM_FACTOR


def simulate_match(
    home_attack: float,
    home_defense: float,
    away_attack: float,
    away_defense: float,
    rng: np.random.Generator,
) -> Dict:
    """
    Simulate one 90-minute match.
    
    Cross-coupling:
      home_rate = home_attack * (away_defense / 1.3)
      away_rate = away_attack * (home_defense / 1.3)
    """
    # Cross-coupled rates
    home_rate = home_attack * (away_defense / 1.3)
    away_rate = away_attack * (home_defense / 1.3)
    
    # Minute-by-minute simulation
    home_timeline = np.zeros(TOTAL_MINUTES, dtype=int)
    away_timeline = np.zeros(TOTAL_MINUTES, dtype=int)
    
    for minute in range(TOTAL_MINUTES):
        home_timeline[minute] = rng.poisson(lambda_profile(home_rate, minute))
        away_timeline[minute] = rng.poisson(lambda_profile(away_rate, minute))
    
    # Compute all stats
    home_goals = int(home_timeline.sum())
    away_goals = int(away_timeline.sum())
    home_ht = int(home_timeline[:HALF_TIME].sum())
    away_ht = int(away_timeline[:HALF_TIME].sum())
    home_2h = home_goals - home_ht
    away_2h = away_goals - away_ht
    
    if home_goals > away_goals:
        result = "Home Win"
    elif home_goals == away_goals:
        result = "Draw"
    else:
        result = "Away Win"
    
    return {
        "home_goals": home_goals,
        "away_goals": away_goals,
        "home_ht": home_ht,
        "away_ht": away_ht,
        "home_2h": home_2h,
        "away_2h": away_2h,
        "result": result,
        "home_timeline": home_timeline,
        "away_timeline": away_timeline,
        "goal_minutes_home": np.where(home_timeline > 0)[0].tolist(),
        "goal_minutes_away": np.where(away_timeline > 0)[0].tolist(),
        "home_rate": home_rate,
        "away_rate": away_rate,
    }


def run_simulations(home_attack, home_defense, away_attack, away_defense,
                    n_sims=10200, seed=42):
    """Run n_sims match simulations."""
    rng = np.random.default_rng(seed)
    results = []
    for _ in range(n_sims):
        results.append(simulate_match(
            home_attack, home_defense, away_attack, away_defense, rng
        ))
    return results


def compute_analytics(results, home_name="Home", away_name="Away"):
    """Compute analytics from simulation results."""
    n = len(results)
    
    home_wins = sum(1 for r in results if r["result"] == "Home Win")
    draws = sum(1 for r in results if r["result"] == "Draw")
    away_wins = n - home_wins - draws
    
    scorelines = [(r["home_goals"], r["away_goals"]) for r in results]
    counts = Counter(scorelines)
    
    avg_home = np.mean([r["home_goals"] for r in results])
    avg_away = np.mean([r["away_goals"] for r in results])
    avg_home_ht = np.mean([r["home_ht"] for r in results])
    avg_away_ht = np.mean([r["away_ht"] for r in results])
    
    return {
        "home_win_pct": home_wins / n * 100,
        "draw_pct": draws / n * 100,
        "away_win_pct": away_wins / n * 100,
        "top10": counts.most_common(10),
        "avg_home_goals": avg_home,
        "avg_away_goals": avg_away,
        "avg_home_ht": avg_home_ht,
        "avg_away_ht": avg_away_ht,
        "n_sims": n,
    }


# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

# ── PART A: Single match test ───────────────────────────────────
print("=== SINGLE MATCH TEST ===")
rng = np.random.default_rng(42)
match = simulate_match(1.3, 0.71, 1.14, 1.29, rng)

print(f"Score: Home {match['home_goals']} - {match['away_goals']} Away")
print(f"Half-Time: Home {match['home_ht']} - {match['away_ht']} Away")
print(f"Result: {match['result']}")
print(f"Home goals in minutes: {match['goal_minutes_home']}")
print(f"Away goals in minutes: {match['goal_minutes_away']}")
print(f"Home rate: {match['home_rate']:.3f}")
print(f"Away rate: {match['away_rate']:.3f}")

# ── PART B: Full simulation run ─────────────────────────────────
print(f"\n=== RUNNING 10,200 SIMULATIONS ===")
results = run_simulations(1.3, 0.71, 1.14, 1.29)
analytics = compute_analytics(results, "Jamaica", "New Caledonia")

print(f"\nJamaica vs New Caledonia — PREDICTION")
print(f"{'='*50}")
print(f"  Jamaica Win:       {analytics['home_win_pct']:.1f}%")
print(f"  Draw:              {analytics['draw_pct']:.1f}%")
print(f"  New Caledonia Win: {analytics['away_win_pct']:.1f}%")
print(f"\n  Expected Goals:")
print(f"    Jamaica:       {analytics['avg_home_goals']:.2f}")
print(f"    New Caledonia: {analytics['avg_away_goals']:.2f}")
print(f"\n  Expected Half-Time:")
print(f"    Jamaica:       {analytics['avg_home_ht']:.2f}")
print(f"    New Caledonia: {analytics['avg_away_ht']:.2f}")
print(f"\n  Top 10 Scorelines:")
for (h, a), cnt in analytics["top10"]:
    pct = cnt / analytics["n_sims"] * 100
    print(f"    Jamaica {h} - {a} New Caledonia: {pct:.1f}%")

# ── PART C: Cross-coupling explanation ──────────────────────────
print(f"\n=== CROSS-COUPLING EXPLAINED ===")
print(f"Jamaica attack: 1.30, New Caledonia defense: 1.29")
print(f"Home rate = 1.30 * (1.29 / 1.3) = {1.30 * (1.29/1.3):.3f}")
print(f"This means: Jamaica's attack is BOOSTED because")
print(f"New Caledonia has a weak defense (concedes 1.29 goals avg)")
print(f"")
print(f"New Caledonia attack: 1.14, Jamaica defense: 0.71")
print(f"Away rate = 1.14 * (0.71 / 1.3) = {1.14 * (0.71/1.3):.3f}")
print(f"This means: New Caledonia's attack is REDUCED because")
print(f"Jamaica has a strong defense (concedes only 0.71 goals avg)")

# ── PART D: Verification ───────────────────────────────────────
print(f"\n=== VERIFICATION ===")
total_pct = analytics["home_win_pct"] + analytics["draw_pct"] + analytics["away_win_pct"]
print(f"Win percentages sum to: {total_pct:.1f}% {'✅' if abs(total_pct-100)<0.1 else '❌'}")
print(f"Simulations run: {analytics['n_sims']} {'✅' if analytics['n_sims']==10200 else '❌'}")