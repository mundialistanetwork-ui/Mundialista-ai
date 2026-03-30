"""
Task 10: NumPy Fundamentals
============================
"""
import numpy as np

# ── PART A: Creating arrays ────────────────────────────────────
goals = np.array([1, 0, 2, 3, 1, 0, 2])
zeros_90 = np.zeros(90, dtype=int)
ones_10 = np.ones(10)
range_90 = np.arange(90)
line = np.linspace(0, 5, 100)

for name, arr in [("goals", goals), ("zeros_90", zeros_90),
                  ("ones_10", ones_10), ("range_90", range_90),
                  ("line", line)]:
    print(f"{name:>10}: shape={arr.shape}, dtype={arr.dtype}, "
          f"first 5={arr[:5]}")

# ── PART B: Array math ─────────────────────────────────────────
print("\n=== ARRAY MATH ===")
print(f"goals = {goals}")
print(f"goals + 1 = {goals + 1}")
print(f"goals * 2 = {goals * 2}")
print(f"goals ** 2 = {goals ** 2}")
print(f"goals / 3 = {goals / 3}")

print(f"\nSum: {goals.sum()}")
print(f"Mean: {goals.mean():.4f}")
print(f"Std: {goals.std():.4f}")
print(f"Max: {goals.max()}")
print(f"Min: {goals.min()}")
print(f"Cumulative sum: {np.cumsum(goals)}")

# ── PART C: Boolean indexing ────────────────────────────────────
mask = goals >= 2
print(f"\n=== BOOLEAN INDEXING ===")
print(f"goals = {goals}")
print(f"mask (goals >= 2) = {mask}")
print(f"goals[mask] = {goals[mask]}")
print(f"Count of 2+ goals: {mask.sum()}")
print(f"Fraction of 2+ goals: {mask.mean():.4f}")

# ── PART D: Simulating a match minute-by-minute ────────────────
timeline = np.zeros(90, dtype=int)
timeline[23] = 1
timeline[67] = 1
timeline[88] = 1

print(f"\n=== MATCH TIMELINE ===")
print(f"Goals per minute (showing non-zero): ", end="")
for minute in range(90):
    if timeline[minute] > 0:
        print(f"min {minute}: {timeline[minute]} goal(s)  ", end="")
print()
print(f"Cumulative goals: {np.cumsum(timeline)[-1]} total")

ht_goals = timeline[:45].sum()
print(f"Half-time goals: {ht_goals}")

sh_goals = timeline[45:].sum()
print(f"Second-half goals: {sh_goals}")

# ── PART E: Working with 2D arrays ─────────────────────────────
results = np.array([
    [2, 1],
    [0, 0],
    [1, 3],
    [3, 1],
    [1, 1],
])

print(f"\n=== 2D ARRAY ===")
print(f"Shape: {results.shape}")
print(f"All home goals: {results[:, 0]}")
print(f"All away goals: {results[:, 1]}")
print(f"Average home goals: {results[:, 0].mean():.2f}")
print(f"Average away goals: {results[:, 1].mean():.2f}")

home_wins = (results[:, 0] > results[:, 1]).sum()
print(f"Home wins: {home_wins} out of {len(results)}")

# ── PART F: np.where ───────────────────────────────────────────
outcomes = np.where(
    results[:, 0] > results[:, 1], 1,
    np.where(results[:, 0] == results[:, 1], 0, -1)
)
print(f"\nOutcomes: {outcomes}")
print(f"Home wins: {(outcomes == 1).sum()}")
print(f"Draws: {(outcomes == 0).sum()}")
print(f"Away wins: {(outcomes == -1).sum()}")