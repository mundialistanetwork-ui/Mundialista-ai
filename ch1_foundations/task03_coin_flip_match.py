"""
Task 03: Categorical Match Outcome Simulation
==============================================
Simulate 10,000 match outcomes using fixed probabilities.
"""
import numpy as np
from collections import Counter

rng = np.random.default_rng(42)

# ── PART A: Define outcome probabilities ────────────────────────
probs = np.array([0.55, 0.25, 0.20])
outcomes = ["Home Win", "Draw", "Away Win"]

# ── PART B: Simulate 10,000 matches ────────────────────────────
simulated_results = rng.choice(outcomes, size=10000, p=probs)

# ── PART C: Count the results ──────────────────────────────────
counts = Counter(simulated_results)
print("=== 10,000 MATCH SIMULATION ===")
for outcome in outcomes:
    count = counts[outcome]
    pct = count / 10000 * 100
    print(f"  {outcome}: {count} ({pct:.1f}%)")

# ── PART D: The Law of Large Numbers ───────────────────────────
print("\n=== LAW OF LARGE NUMBERS ===")
print(f"{'Sample Size':<15} {'Home Win %':<15} {'Diff from 55%'}")
print("-" * 45)

for n in [10, 100, 1000, 10000, 100000]:
    rng_temp = np.random.default_rng(42)
    sims = rng_temp.choice(outcomes, size=n, p=probs)
    hw_count = sum(1 for s in sims if s == "Home Win")
    hw_pct = hw_count / n * 100
    diff = abs(hw_pct - 55.0)
    print(f"{n:<15} {hw_pct:<15.1f} {diff:.1f}%")

# ── PART E: Why 10,200 simulations? ────────────────────────────
print("\n=== WHY 10,200 SIMULATIONS? ===")
print("Yes, 10,200 is enough for stable probability estimates.")
print("As we saw above, by 10,000 simulations the percentages")
print("are very close to the true probabilities.")
print("With only 50 simulations, the results would be very noisy")
print("and unreliable — you might get 70% home wins one time")
print("and 40% the next time. More simulations = more stability.")