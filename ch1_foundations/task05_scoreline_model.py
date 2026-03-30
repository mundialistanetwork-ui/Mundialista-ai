"""
Task 05: Bivariate Independent Poisson Scoreline Model
======================================================
"""
import numpy as np
from scipy.stats import poisson
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# ── PART A: Compute the full scoreline probability matrix ──────
lam_home = 1.3
lam_away = 0.8

matrix = np.zeros((7, 7))
for a in range(7):
    for h in range(7):
        matrix[a, h] = poisson.pmf(h, mu=lam_home) * poisson.pmf(a, mu=lam_away)

print("=== SCORELINE PROBABILITY MATRIX (%) ===")
print(f"{'':>8}", end="")
for h in range(7):
    print(f"H={h:>5}", end="  ")
print()
for a in range(7):
    print(f"A={a:<5}", end="  ")
    for h in range(7):
        print(f"{matrix[a, h]*100:>6.2f}%", end=" ")
    print()

# ── PART B: Answer questions ───────────────────────────────────
# Most likely scoreline
max_idx = np.unravel_index(matrix.argmax(), matrix.shape)
print(f"\n=== ANSWERS ===")
print(f"1. Most likely scoreline: {max_idx[1]}-{max_idx[0]} "
      f"({matrix[max_idx]*100:.2f}%)")
print(f"2. P(0-0) = {matrix[0,0]*100:.2f}%")

home_win = sum(matrix[a, h] for a in range(7) for h in range(7) if h > a)
draw = sum(matrix[a, h] for a in range(7) for h in range(7) if h == a)
away_win = sum(matrix[a, h] for a in range(7) for h in range(7) if h < a)

print(f"3. P(Home Win) = {home_win*100:.1f}%")
print(f"4. P(Draw) = {draw*100:.1f}%")
print(f"5. P(Away Win) = {away_win*100:.1f}%")
print(f"6. Sum = {(home_win + draw + away_win)*100:.1f}%")

# ── PART C: Visualize as a heatmap ─────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(matrix * 100, annot=True, fmt=".1f", cmap="YlOrRd",
            xticklabels=[f"{h}" for h in range(7)],
            yticklabels=[f"{a}" for a in range(7)],
            ax=ax)
ax.set_xlabel("Home Goals (Jamaica)")
ax.set_ylabel("Away Goals (New Caledonia)")
ax.set_title("Scoreline Probability Matrix (%)")
plt.tight_layout()
plt.savefig("task05_scoreline_heatmap.png", dpi=150)
plt.show()

# ── PART D: Simulate 10,000 matches ────────────────────────────
rng = np.random.default_rng(42)
home_goals = rng.poisson(1.3, size=10000)
away_goals = rng.poisson(0.8, size=10000)

scorelines = list(zip(home_goals, away_goals))
counts = Counter(scorelines)

print("\n=== TOP 5 SIMULATED SCORELINES ===")
for (h, a), count in counts.most_common(5):
    sim_pct = count / 10000 * 100
    formula_pct = poisson.pmf(h, mu=1.3) * poisson.pmf(a, mu=0.8) * 100
    print(f"  {h}-{a}: Simulated={sim_pct:.1f}%, Formula={formula_pct:.1f}%")

# ── PART E: The independence assumption ─────────────────────────
print("\n=== INDEPENDENCE ASSUMPTION ===")
print("In real football, independence is NOT perfectly true.")
print("Example: If a team goes 1-0 up early, they might play")
print("more defensively while the losing team pushes forward.")
print("This changes both teams' effective scoring rates.")
print("However, independence is a good enough approximation")
print("that the model still works well in practice.")