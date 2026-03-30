"""
Task 12: Your First PyMC Model
===============================
Estimate Jamaica's goal-scoring rate from observed data.
"""
import pymc as pm
import numpy as np
import arviz as az
import matplotlib.pyplot as plt

# Observed: Jamaica scored these goals in their last 7 matches
observed_goals = np.array([1, 2, 1, 0, 3, 2, 1])

# ── PART A: Define the model ───────────────────────────────────
with pm.Model() as jamaica_model:
    # Prior
    lambda_attack = pm.TruncatedNormal(
        "lambda_attack", mu=1.3, sigma=0.5, lower=0.05, upper=6.0
    )
    
    # Likelihood
    obs = pm.Poisson(
        "observed_goals_likelihood", mu=lambda_attack, observed=observed_goals
    )

# ── PART B: Sample from the posterior ───────────────────────────
print("Sampling from posterior... (this may take a minute)")
with jamaica_model:
    trace = pm.sample(
        draws=2000,
        tune=1000,
        chains=2,
        cores=1,
        random_seed=42,
        return_inferencedata=True,
        progressbar=True,
    )

# ── PART C: Examine the trace ──────────────────────────────────
print("\n=== POSTERIOR SUMMARY ===")
print(az.summary(trace, var_names=["lambda_attack"]))

# ── PART D: Plot the posterior ──────────────────────────────────
az.plot_posterior(trace, var_names=["lambda_attack"])
plt.tight_layout()
plt.savefig("task12_pymc_posterior.png", dpi=150)
plt.show()
print("Saved: task12_pymc_posterior.png")

# ── PART E: Plot the trace ─────────────────────────────────────
az.plot_trace(trace, var_names=["lambda_attack"])
plt.tight_layout()
plt.savefig("task12_pymc_trace.png", dpi=150)
plt.show()
print("Saved: task12_pymc_trace.png")

# ── PART F: Compare with grid approximation ────────────────────
samples = trace.posterior["lambda_attack"].values.flatten()
pymc_mean = samples.mean()
pymc_std = samples.std()

print(f"\n=== COMPARISON ===")
print(f"Data mean: {observed_goals.mean():.3f}")
print(f"Prior mean: 1.300")
print(f"PyMC posterior mean: {pymc_mean:.3f}")
print(f"PyMC posterior std: {pymc_std:.3f}")
print(f"(Posterior mean should be between prior mean and data mean)")

# ── PART G: Questions ──────────────────────────────────────────
print(f"\n=== ANSWERS ===")
print("1. tune=1000 is the 'warmup' period. The sampler needs time")
print("   to find the right region of parameter space. These early")
print("   samples are unreliable and are discarded.")
print("2. chains=2 means two independent random walks. If both")
print("   chains find the same posterior, we're confident the")
print("   sampler converged to the right answer.")
print("3. r_hat ≈ 1.0 means all chains agree — good convergence.")
print("   r_hat > 1.05 would mean chains disagree — bad sign.")
print("4. If prior was Normal(3.0, 0.2), the posterior would be")
print("   pulled HIGHER toward 3.0. With σ=0.2 (very confident),")
print("   even the data couldn't fully overcome the strong prior.")