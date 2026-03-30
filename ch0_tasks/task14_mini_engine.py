"""
Task 14: Mini Prediction Engine
================================
The complete prediction pipeline in its simplest form.
"""
import numpy as np
from collections import Counter

def get_team_rate(goals_list: list) -> float:
    """Compute average goal rate from recent matches."""
    return sum(goals_list) / len(goals_list)


def simulate_match(home_rate: float, away_rate: float,
                   rng: np.random.Generator) -> dict:
    """Simulate one match using simple Poisson draws."""
    home_goals = rng.poisson(home_rate)
    away_goals = rng.poisson(away_rate)
    return {"home": int(home_goals), "away": int(away_goals)}


def run_simulations(home_rate: float, away_rate: float,
                    n_sims: int, seed: int = 42) -> list:
    """Run n_sims match simulations."""
    rng = np.random.default_rng(seed)
    results = []
    for _ in range(n_sims):
        results.append(simulate_match(home_rate, away_rate, rng))
    return results


def analyze_results(results: list) -> dict:
    """Compute analytics from simulation results."""
    n = len(results)
    scorelines = [(r["home"], r["away"]) for r in results]
    counts = Counter(scorelines)
    
    home_wins = sum(1 for r in results if r["home"] > r["away"])
    draws = sum(1 for r in results if r["home"] == r["away"])
    away_wins = n - home_wins - draws
    
    return {
        "home_win_pct": home_wins / n * 100,
        "draw_pct": draws / n * 100,
        "away_win_pct": away_wins / n * 100,
        "top5": counts.most_common(5),
        "avg_home": np.mean([r["home"] for r in results]),
        "avg_away": np.mean([r["away"] for r in results]),
    }


def display_results(analytics: dict, home: str, away: str):
    """Print formatted results."""
    print(f"\n{'='*50}")
    print(f"  {home} vs {away} — PREDICTION")
    print(f"{'='*50}")
    print(f"  {home} Win: {analytics['home_win_pct']:.1f}%")
    print(f"  Draw:        {analytics['draw_pct']:.1f}%")
    print(f"  {away} Win:  {analytics['away_win_pct']:.1f}%")
    print(f"\n  Most Likely Scorelines:")
    for (h, a), cnt in analytics["top5"]:
        print(f"    {home} {h} - {a} {away}: "
              f"{cnt/10200*100:.1f}%")
    print(f"\n  Expected Goals:")
    print(f"    {home}: {analytics['avg_home']:.2f}")
    print(f"    {away}: {analytics['avg_away']:.2f}")
    print(f"{'='*50}")


# ══════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Step 1: Data
    jamaica_goals = [1, 0, 2, 1, 0, 3, 2]
    newcal_goals = [1, 0, 2, 1, 0, 1, 3]
    
    # Step 2: Compute rates
    home_rate = get_team_rate(jamaica_goals)
    away_rate = get_team_rate(newcal_goals)
    print(f"Jamaica rate: {home_rate:.2f} goals/match")
    print(f"New Caledonia rate: {away_rate:.2f} goals/match")
    
    # Step 3: Simulate
    print(f"\nRunning 10,200 simulations...")
    results = run_simulations(home_rate, away_rate, n_sims=10200)
    print(f"Done!")
    
    # Step 4: Analyze
    analytics = analyze_results(results)
    
    # Step 5: Display
    display_results(analytics, "Jamaica", "New Caledonia")