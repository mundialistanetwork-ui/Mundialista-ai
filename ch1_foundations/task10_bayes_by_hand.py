"""
Task 10: Bayes' Theorem — Step by Step
=======================================
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson

# SCENARIO:
# Jamaica's true goal-scoring rate λ is unknown.
# We think it's one of: [0.5, 1.0, 1.5, 2.0, 2.5]
# Prior: uniform (20% each)
# Observed: Jamaica scored 1, 2, 1 goals in 3 matches

possible_lambdas = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
prior = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
observed_goals = [1, 2, 1]

# ── PART A: Compute likelihood for each λ ──────────────────────
likelihoods = np.ones(5)
for lam_idx, lam in enumerate(possible_lambdas):
    for g in observed_goals:
        likelihoods[lam_idx] *= poisson.pmf(g, mu=lam)

print("=== PART A: LIKELIHOODS ===")
print(f"{'λ':<8} {'P(data|λ)':<15}")
print("-" * 23)
for lam, lik in zip(possible_lambdas, likelihoods):
    print(f"{lam:<8} {lik:<15.6f}")

# ── PART B: Unnormalized posterior ──────────────────────────────
unnormalized = prior * likelihoods

print("\n=== PART B: UNNORMALIZED POSTERIOR ===")
for lam, u in zip(possible_lambdas, unnormalized):
    print(f"λ={lam}: {u:.6f}")

# ── PART C: Normalize to get true posterior ─────────────────────
posterior = unnormalized / unnormalized.sum()

print("\n=== PART C: FULL BAYES TABLE ===")
print(f"{'λ':<8} {'Prior':<10} {'Likelihood':<15} {'Posterior':<10}")
print("-" * 43)
for lam, pr, lik, post in zip(possible_lambdas, prior, likelihoods, posterior):
    print(f"{lam:<8} {pr:<10.2f} {lik:<15.6f} {post:<10.4f}")
print(f"\nPosterior sums to: {posterior.sum():.4f}")

# ── PART D: Visualize prior vs posterior ────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
width = 0.15
x = np.arange(len(possible_lambdas))
ax.bar(x - width/2, prior, width, color="blue", alpha=0.7, label="Prior")
ax.bar(x + width/2, posterior, width, color="red", alpha=0.7, label="Posterior")
ax.set_xticks(x)
ax.set_xticklabels(possible_lambdas)
ax.set_xlabel("λ (goals per match)", fontsize=12)
ax.set_ylabel("Probability", fontsize=12)
ax.set_title("Bayesian Update: Prior vs Posterior", fontsize=14)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("task10_bayes_update.png", dpi=150)
plt.show()
print("Saved: task10_bayes_update.png")

# ── PART E: What did we learn? ──────────────────────────────────
best_lambda = possible_lambdas[posterior.argmax()]
print(f"\n=== WHAT WE LEARNED ===")
print(f"1. Highest posterior probability: λ = {best_lambda}")
print(f"2. Yes! The data shifted our belief from uniform (all equal)")
print(f"   to peaked around λ = {best_lambda}.")
print(f"3. Observed goals averaged {np.mean(observed_goals):.2f}.")
print(f"   The posterior IS peaked near that value, because the")
print(f"   likelihood is highest for λ values close to the data mean.")
print(f"4. With 10 more matches of 1 goal each, the posterior would")
print(f"   get MUCH sharper — more data = more certainty = narrower peak.")