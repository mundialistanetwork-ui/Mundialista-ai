"""
Task 09: Understanding Prior Distributions
==========================================
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, truncnorm

# ── PART A: Plot three different priors ─────────────────────────
x = np.linspace(0, 4, 500)

fig, ax = plt.subplots(figsize=(10, 5))

for sigma, color, label in [(0.2, "blue", "Confident (σ=0.2)"),
                              (0.5, "green", "Moderate (σ=0.5)"),
                              (1.0, "red", "Uncertain (σ=1.0)")]:
    y = norm.pdf(x, loc=1.3, scale=sigma)
    ax.plot(x, y, color=color, linewidth=2, label=label)

ax.set_xlabel("λ (goals per match)", fontsize=12)
ax.set_ylabel("Probability Density", fontsize=12)
ax.set_title("Three Different Priors for Jamaica's Attack Rate", fontsize=14)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("task09_priors.png", dpi=150)
plt.show()
print("Saved: task09_priors.png")

# ── PART B: Truncated Normal ───────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))

# Regular normal
y_normal = norm.pdf(x, loc=1.3, scale=0.5)
ax.plot(x, y_normal, color="blue", linewidth=2, linestyle="--",
        label="Normal(1.3, 0.5)")

# Truncated normal (lower=0.05, upper=6.0)
a_trunc = (0.05 - 1.3) / 0.5
b_trunc = (6.0 - 1.3) / 0.5
y_trunc = truncnorm.pdf(x, a_trunc, b_trunc, loc=1.3, scale=0.5)
ax.plot(x, y_trunc, color="red", linewidth=2,
        label="TruncatedNormal(1.3, 0.5, lower=0.05, upper=6.0)")

ax.set_xlabel("λ (goals per match)", fontsize=12)
ax.set_ylabel("Probability Density", fontsize=12)
ax.set_title("Normal vs Truncated Normal Prior", fontsize=14)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("task09_truncated.png", dpi=150)
plt.show()
print("Saved: task09_truncated.png")

# ── PART C: Different priors comparison ─────────────────────────
rng = np.random.default_rng(42)

print("\n=== ANALYST COMPARISON (σ=0.3) ===")
samples_a = rng.normal(1.3, 0.3, size=10000)
samples_b = rng.normal(0.8, 0.3, size=10000)
print(f"Analyst A (prior 1.3): mean = {samples_a.mean():.3f}")
print(f"Analyst B (prior 0.8): mean = {samples_b.mean():.3f}")
print(f"Difference: {abs(samples_a.mean() - samples_b.mean()):.3f}")

print("\n=== ANALYST COMPARISON (σ=1.0) ===")
samples_a2 = rng.normal(1.3, 1.0, size=10000)
samples_b2 = rng.normal(0.8, 1.0, size=10000)
print(f"Analyst A (prior 1.3): mean = {samples_a2.mean():.3f}")
print(f"Analyst B (prior 0.8): mean = {samples_b2.mean():.3f}")
print(f"Difference: {abs(samples_a2.mean() - samples_b2.mean()):.3f}")
print("With wider priors (σ=1.0), the means are similar because")
print("there's more overlap between the two distributions.")

# ── PART D: Connecting to our engine ────────────────────────────
print("\n=== CONNECTION TO ENGINE ===")
print("1. The prior center (mu) comes from the team's historical")
print("   average goals scored (stats_home['avg_gf']).")
print("2. The prior width (sigma) comes from the standard deviation")
print("   of their recent goals (stats_home['std_gf']).")
print("3. max(..., 0.3) prevents sigma from being 0 or tiny.")
print("   If σ=0, the prior would be a spike at one value,")
print("   allowing NO learning from data — the posterior would")
print("   just be the prior, ignoring all evidence.")