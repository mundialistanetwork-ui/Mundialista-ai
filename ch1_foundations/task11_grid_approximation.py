"""
Task 11: Grid Approximation for Continuous Bayesian Inference
=============================================================
"""
import numpy as np
from scipy.stats import poisson, norm
import matplotlib.pyplot as plt

# ── PART A: Create a fine grid of λ values ──────────────────────
grid = np.linspace(0.01, 5.0, 1000)

# ── PART B: Define the prior ───────────────────────────────────
prior = norm.pdf(grid, loc=1.3, scale=0.5)
prior = np.where(grid > 0, prior, 0)
prior = prior / prior.sum()

# ── PART C: Compute likelihood over the grid ───────────────────
observed = np.array([1, 2, 1, 0, 3, 2, 1])

likelihood = np.ones_like(grid)
for g in observed:
    likelihood *= poisson.pmf(g, mu=grid)

# ── PART D: Compute and normalize the posterior ─────────────────
unnormalized_posterior = prior * likelihood
posterior = unnormalized_posterior / unnormalized_posterior.sum()

# ── PART E: Plot prior, likelihood, and posterior ───────────────
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

axes[0].plot(grid, prior, color="blue", linewidth=2)
axes[0].fill_between(grid, prior, alpha=0.3, color="blue")
axes[0].set_ylabel("Density")
axes[0].set_title("Prior: Normal(1.3, 0.5)")

axes[1].plot(grid, likelihood / likelihood.max(), color="green", linewidth=2)
axes[1].fill_between(grid, likelihood / likelihood.max(), alpha=0.3, color="green")
axes[1].set_ylabel("Scaled Likelihood")
axes[1].set_title("Likelihood: P(data | λ)")

axes[2].plot(grid, posterior, color="red", linewidth=2)
axes[2].fill_between(grid, posterior, alpha=0.3, color="red")
axes[2].set_ylabel("Density")
axes[2].set_xlabel("λ (goals per match)")
axes[2].set_title("Posterior: P(λ | data)")

plt.tight_layout()
plt.savefig("task11_grid_bayes.png", dpi=150)
plt.show()
print("Saved: task11_grid_bayes.png")

# ── PART F: Extract summary statistics ──────────────────────────
posterior_mean = np.sum(grid * posterior)
posterior_mode = grid[np.argmax(posterior)]

# 90% credible interval
cumsum = np.cumsum(posterior)
lower_idx = np.searchsorted(cumsum, 0.05)
upper_idx = np.searchsorted(cumsum, 0.95)
ci_lower = grid[lower_idx]
ci_upper = grid[upper_idx]

print(f"\n=== POSTERIOR SUMMARY ===")
print(f"Posterior Mean: {posterior_mean:.3f}")
print(f"Posterior Mode: {posterior_mode:.3f}")
print(f"90% Credible Interval: [{ci_lower:.3f}, {ci_upper:.3f}]")
print(f"Data Mean: {observed.mean():.3f}")
print(f"Prior Mean: 1.300")
print(f"(Posterior is between prior and data mean — pulled by both!)")

# ── PART G: Sequential updating ────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))

colors = plt.cm.viridis(np.linspace(0, 1, len(observed) + 1))

# Start with the prior
current_prior = prior.copy()
ax.plot(grid, current_prior, color=colors[0], linewidth=1.5,
        label="Prior", linestyle="--")

for i, g in enumerate(observed):
    # Likelihood for this single observation
    single_likelihood = poisson.pmf(g, mu=grid)
    
    # Update
    unnorm = current_prior * single_likelihood
    current_posterior = unnorm / unnorm.sum()
    
    ax.plot(grid, current_posterior, color=colors[i + 1], linewidth=1.5,
            label=f"After match {i+1} (scored {g})")
    
    # This posterior becomes the next prior
    current_prior = current_posterior.copy()

ax.set_xlabel("λ (goals per match)", fontsize=12)
ax.set_ylabel("Probability", fontsize=12)
ax.set_title("Sequential Bayesian Updating: Watch Beliefs Sharpen!", fontsize=14)
ax.legend(fontsize=8, loc="upper right")
plt.tight_layout()
plt.savefig("task11_sequential_update.png", dpi=150)
plt.show()
print("Saved: task11_sequential_update.png")
print("\nKey insight: The posterior gets narrower with each match observed!")
print("More data = more certainty about Jamaica's true scoring rate.")