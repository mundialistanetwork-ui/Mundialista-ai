"""
Task 07: Minute-by-Minute Match Simulation
==========================================
"""
import numpy as np
import matplotlib.pyplot as plt

TOTAL_MINUTES = 90
HALF_TIME = 45

def lambda_profile(base_rate: float, minute: int) -> float:
    """Return the instantaneous goal rate for one minute."""
    multipliers = {
        range(0, 15): 0.85,
        range(15, 45): 1.00,
        range(45, 60): 1.10,
        range(60, 80): 1.05,
        range(80, 90): 1.30,
    }
    
    m = 1.0
    for minute_range, mult in multipliers.items():
        if minute in minute_range:
            m = mult
            break
    
    raw = (base_rate / 90) * m
    # Normalization factor (precomputed so all 90 minutes sum to base_rate)
    norm_factor = sum(
        (base_rate / 90) * (0.85 if i < 15 else 1.00 if i < 45 else 
         1.10 if i < 60 else 1.05 if i < 80 else 1.30)
        for i in range(90)
    )
    return raw * (base_rate / norm_factor)


def simulate_one_match(home_rate, away_rate, rng):
    """Simulate a single match minute-by-minute."""
    home_timeline = np.zeros(TOTAL_MINUTES, dtype=int)
    away_timeline = np.zeros(TOTAL_MINUTES, dtype=int)

    for minute in range(TOTAL_MINUTES):
        home_timeline[minute] = rng.poisson(lambda_profile(home_rate, minute))
        away_timeline[minute] = rng.poisson(lambda_profile(away_rate, minute))

    return {
        "home_goals": int(home_timeline.sum()),
        "away_goals": int(away_timeline.sum()),
        "home_ht": int(home_timeline[:HALF_TIME].sum()),
        "away_ht": int(away_timeline[:HALF_TIME].sum()),
        "home_timeline": home_timeline,
        "away_timeline": away_timeline,
        "goal_minutes_home": np.where(home_timeline > 0)[0].tolist(),
        "goal_minutes_away": np.where(away_timeline > 0)[0].tolist(),
    }


# ── PART B: Simulate and print one match ───────────────────────
rng = np.random.default_rng(42)
result = simulate_one_match(1.3, 0.8, rng)

print("=== SINGLE MATCH SIMULATION ===")
print(f"Final Score: Home {result['home_goals']} - "
      f"{result['away_goals']} Away")
print(f"Half-Time:   Home {result['home_ht']} - "
      f"{result['away_ht']} Away")
print(f"Home goals in minutes: {result['goal_minutes_home']}")
print(f"Away goals in minutes: {result['goal_minutes_away']}")

# ── PART C: Simulate 100 matches ───────────────────────────────
home_wins = 0
draws = 0
away_wins = 0
total_home = 0
total_away = 0

for _ in range(100):
    r = simulate_one_match(1.3, 0.8, rng)
    total_home += r["home_goals"]
    total_away += r["away_goals"]
    if r["home_goals"] > r["away_goals"]:
        home_wins += 1
    elif r["home_goals"] == r["away_goals"]:
        draws += 1
    else:
        away_wins += 1

print(f"\n=== 100 MATCH SUMMARY ===")
print(f"Avg Score: {total_home/100:.2f} - {total_away/100:.2f}")
print(f"Home Wins: {home_wins}%, Draws: {draws}%, Away Wins: {away_wins}%")

# ── PART D: Plot match timeline ─────────────────────────────────
rng2 = np.random.default_rng(123)
result2 = simulate_one_match(1.3, 0.8, rng2)

fig, ax = plt.subplots(figsize=(12, 4))
minutes = np.arange(90)
ax.bar(minutes, result2["home_timeline"], color="green", alpha=0.7, label="Home Goals")
ax.bar(minutes, -result2["away_timeline"], color="orange", alpha=0.7, label="Away Goals")
ax.axvline(x=45, color="gray", linestyle=":", label="Half-time")
ax.set_xlabel("Minute")
ax.set_ylabel("Goals")
ax.set_title(f"Match Timeline: Home {result2['home_goals']} - {result2['away_goals']} Away")
ax.legend()
plt.tight_layout()
plt.savefig("task07_match_timeline.png", dpi=150)
plt.show()
print("Saved: task07_match_timeline.png")

# ── PART E: Flat vs Variable profile comparison ────────────────
def simulate_flat(home_rate, away_rate, rng):
    """Simulate with flat profile (equal rate every minute)."""
    ht = np.zeros(90, dtype=int)
    at = np.zeros(90, dtype=int)
    for m in range(90):
        ht[m] = rng.poisson(home_rate / 90)
        at[m] = rng.poisson(away_rate / 90)
    return {
        "home_1h": int(ht[:45].sum()), "home_2h": int(ht[45:].sum()),
        "away_1h": int(at[:45].sum()), "away_2h": int(at[45:].sum()),
        "home_last10": int(ht[80:].sum()), "away_last10": int(at[80:].sum()),
    }

rng_flat = np.random.default_rng(42)
rng_var = np.random.default_rng(42)

flat_1h, flat_2h, flat_last10 = 0, 0, 0
var_1h, var_2h, var_last10 = 0, 0, 0

for _ in range(5000):
    f = simulate_flat(1.3, 0.8, rng_flat)
    flat_1h += f["home_1h"]
    flat_2h += f["home_2h"]
    flat_last10 += f["home_last10"]
    
    v = simulate_one_match(1.3, 0.8, rng_var)
    var_1h += v["home_ht"]
    var_2h += v["home_goals"] - v["home_ht"]
    var_last10 += int(v["home_timeline"][80:].sum())

print(f"\n=== FLAT vs VARIABLE (5000 matches, home team) ===")
print(f"{'Metric':<20} {'Flat':<12} {'Variable'}")
print("-" * 44)
print(f"{'Avg 1H goals':<20} {flat_1h/5000:<12.3f} {var_1h/5000:.3f}")
print(f"{'Avg 2H goals':<20} {flat_2h/5000:<12.3f} {var_2h/5000:.3f}")
print(f"{'Avg last 10 min':<20} {flat_last10/5000:<12.3f} {var_last10/5000:.3f}")