"""
Task 04: The Poisson Distribution for Goal Scoring
===================================================
"""
import numpy as np
from scipy.stats import poisson
from collections import Counter
import matplotlib.pyplot as plt
import math

# ── PART A: Manual Poisson calculation ──────────────────────────
lam = 1.3

print("=== MANUAL POISSON CALCULATION (λ = 1.3) ===")
print(f"{'k (goals)':<12} {'P(X = k)':<15} {'Percentage':<10}")
print("-" * 37)

manual_probs = []
for k in range(6):
    p = (lam**k * math.exp(-lam)) / math.factorial(k)
    manual_probs.append(p)
    print(f"{k:<12} {p:<15.6f} {p*100:<10.2f}%")

print(f"\nSum of P(0..5) = {sum(manual_probs):.6f}")
print(f"P(6 or more) = {1 - sum(manual_probs):.6f}")

# ── PART B: Verify with scipy ──────────────────────────────────
print("\n=== VERIFICATION WITH SCIPY ===")
print(f"{'k':<6} {'Manual':<15} {'Scipy':<15} {'Match?'}")
print("-" * 42)
for k in range(6):
    scipy_p = poisson.pmf(k, mu=lam)
    match = "✅" if abs(manual_probs[k] - scipy_p) < 0.0000001 else "❌"
    print(f"{k:<6} {manual_probs[k]:<15.6f} {scipy_p:<15.6f} {match}")

# ── PART C: Visualize the distribution ──────────────────────────
lambdas = [0.8, 1.3, 2.5]
colors = ["#1b9e77", "#d95f02", "#7570b3"]
labels = ["Weak attack (λ=0.8)", "Average (λ=1.3)", "Strong (λ=2.5)"]
k_values = np.arange(0, 8)

fig, ax = plt.subplots(figsize=(10, 5))

width = 0.25
for i, (l, color, label) in enumerate(zip(lambdas, colors, labels)):
    probs = [poisson.pmf(k, mu=l) for k in k_values]
    ax.bar(k_values + i*width - width, probs, width=width,
           color=color, label=label)

ax.set_xlabel("Goals Scored", fontsize=12)
ax.set_ylabel("Probability", fontsize=12)
ax.set_title("Poisson Goal Distribution for Different Team Strengths",
             fontsize=14, fontweight="bold")
ax.set_xticks(k_values)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("task04_poisson_plot.png", dpi=150)
plt.show()
print("Saved: task04_poisson_plot.png")

# ── PART D: Sampling vs Formula ─────────────────────────────────
rng = np.random.default_rng(42)
samples = rng.poisson(1.3, size=100000)
counts = Counter(samples)

print("\n=== SAMPLING vs FORMULA (λ = 1.3, 100,000 samples) ===")
print(f"{'k':<6} {'Formula':<12} {'Sampled':<12} {'Difference'}")
print("-" * 42)
for k in range(6):
    formula_p = poisson.pmf(k, mu=1.3)
    sampled_p = counts[k] / 100000
    diff = abs(formula_p - sampled_p)
    print(f"{k:<6} {formula_p:<12.4f} {sampled_p:<12.4f} {diff:.4f}")

# ── PART E: Key insight ────────────────────────────────────────
print("\n=== KEY INSIGHT ===")
p_a_zero = poisson.pmf(0, mu=1.3)
p_b_zero = poisson.pmf(0, mu=0.8)
print(f"P(Team A scores 0) with λ=1.3: {p_a_zero:.4f} ({p_a_zero*100:.1f}%)")
print(f"P(Team B scores 0) with λ=0.8: {p_b_zero:.4f} ({p_b_zero*100:.1f}%)")
print(f"Team B (weaker, λ=0.8) is MORE likely to be shut out.")
print(f"A higher λ does NOT guarantee more goals in a single match.")
print(f"It just makes higher scores more probable on average.")