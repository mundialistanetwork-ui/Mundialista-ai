"""
Task 02: Random Number Generator Basics
========================================
Learn: seeds, uniform random numbers, and why reproducibility matters.
"""
import numpy as np

# ── PART A: Create a random number generator with seed 42 ──────
rng = np.random.default_rng(42)

# ── PART B: Generate 10 random integers between 0 and 5 ────────
goals_b = rng.integers(0, 6, size=10)
print(f"Part B: {goals_b}")

# ── PART C: Run again (same rng, do NOT reset) ─────────────────
goals_c = rng.integers(0, 6, size=10)
print(f"Part C: {goals_c}")
print(f"Same as Part B? {np.array_equal(goals_b, goals_c)}")

# ── PART D: NEW rng with SAME seed (42) ────────────────────────
rng2 = np.random.default_rng(42)
goals_d = rng2.integers(0, 6, size=10)
print(f"Part D: {goals_d}")
print(f"Same as Part B? {np.array_equal(goals_b, goals_d)}")

# ── PART E: rng with seed 99 ───────────────────────────────────
rng3 = np.random.default_rng(99)
goals_e = rng3.integers(0, 6, size=10)
print(f"Part E: {goals_e}")
print(f"Same as Part B? {np.array_equal(goals_b, goals_e)}")

# ── PART F: Reflection ─────────────────────────────────────────
print("\n=== REFLECTIONS ===")
print("1. We use seeds so that results are reproducible. Anyone running")
print("   the same code with the same seed gets the exact same results.")
print("2. Yes, two people with the same seed will get identical results.")
print("3. Our engine uses SEED = 42 so that every time we run it, we get")
print("   the same predictions. This makes debugging and testing possible.")