"""
Task 14: MCMC Diagnostics — Can We Trust Our Samples?
=====================================================
"""
import pymc as pm
import numpy as np
import arviz as az
import matplotlib.pyplot as plt

observed = np.array([1, 2, 1, 0, 3, 2, 1])

# ── PART A: Good model — sufficient tuning ─────────────────────
print("Running GOOD model...")
with pm.Model() as good_model:
    lam = pm.TruncatedNormal("lam", mu=1.3, sigma=0.5,
                              lower=0.05, upper=6.0)
    obs = pm.Poisson("obs", mu=lam, observed=observed)
    trace_good = pm.sample(draws=2000, tune=1000, chains=4,
                           cores=1, random_seed=42,
                           return_inferencedata=True,
                           progressbar=True)

# ── PART B: Bad model — insufficient tuning ─────────────────────
print("\nRunning BAD model...")
with pm.Model() as bad_model:
    lam = pm.TruncatedNormal("lam", mu=1.3, sigma=0.5,
                              lower=0.05, upper=6.0)
    obs = pm.Poisson("obs", mu=lam, observed=observed)
    trace_bad = pm.sample(draws=50, tune=5, chains=2,
                          cores=1, random_seed=42,
                          return_inferencedata=True,
                          progressbar=True)

# ── PART C: Compare diagnostics ────────────────────────────────
print("\n=== GOOD MODEL DIAGNOSTICS ===")
print(az.summary(trace_good, var_names=["lam"]))
print("\n=== BAD MODEL DIAGNOSTICS ===")
print(az.summary(trace_bad, var_names=["lam"]))

# ── PART D: Plot trace comparisons ─────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Good model - posterior
good_samples = trace_good.posterior["lam"].values.flatten()
axes[0, 0].hist(good_samples, bins=50, color="steelblue",
                edgecolor="black", alpha=0.7)
axes[0, 0].set_title("Good Model — Posterior")
axes[0, 0].axvline(good_samples.mean(), color="red", linestyle="--")

# Good model - trace
for chain in range(4):
    chain_samples = trace_good.posterior["lam"].values[chain]
    axes[0, 1].plot(chain_samples, alpha=0.5, linewidth=0.5)
axes[0, 1].set_title("Good Model — Trace (4 chains)")
axes[0, 1].set_xlabel("Sample")

# Bad model - posterior
bad_samples = trace_bad.posterior["lam"].values.flatten()
axes[1, 0].hist(bad_samples, bins=20, color="salmon",
                edgecolor="black", alpha=0.7)
axes[1, 0].set_title("Bad Model — Posterior")
axes[1, 0].axvline(bad_samples.mean(), color="red", linestyle="--")

# Bad model - trace
for chain in range(2):
    chain_samples = trace_bad.posterior["lam"].values[chain]
    axes[1, 1].plot(chain_samples, alpha=0.7, linewidth=1)
axes[1, 1].set_title("Bad Model — Trace (2 chains)")
axes[1, 1].set_xlabel("Sample")

plt.tight_layout()
plt.savefig("task14_diagnostics_comparison.png", dpi=150)
plt.show()
print("Saved: task14_diagnostics_comparison.png")

# ── PART E: Diagnostic checklist ───────────────────────────────
good_summary = az.summary(trace_good, var_names=["lam"])
bad_summary = az.summary(trace_bad, var_names=["lam"])

print("\n=== DIAGNOSTIC CHECKLIST ===")
print("\nGOOD MODEL:")
print(f"  1. r_hat: {good_summary['r_hat'].values[0]:.3f} — "
      f"{'✅ < 1.01' if good_summary['r_hat'].values[0] < 1.01 else '❌ > 1.01'}")
print(f"  2. ESS bulk: {good_summary['ess_bulk'].values[0]:.0f} — "
      f"{'✅ > 400' if good_summary['ess_bulk'].values[0] > 400 else '❌ < 400'}")
print(f"  3. Trace: Should look like fuzzy caterpillars ✅")
print(f"  4. Trust predictions? YES ✅")

print("\nBAD MODEL:")
print(f"  1. r_hat: {bad_summary['r_hat'].values[0]:.3f} — "
      f"{'✅ < 1.01' if bad_summary['r_hat'].values[0] < 1.01 else '⚠️ may be > 1.01'}")
print(f"  2. ESS bulk: {bad_summary['ess_bulk'].values[0]:.0f} — "
      f"{'✅ > 400' if bad_summary['ess_bulk'].values[0] > 400 else '❌ < 400'}")
print(f"  3. Trace: Likely jagged and unstable ❌")
print(f"  4. Trust predictions? NO ❌ — not enough samples")

print("\n=== KEY TAKEAWAYS ===")
print("- More draws and tuning = better convergence")
print("- Multiple chains help verify the sampler found the right answer")
print("- Always check r_hat < 1.01 and ESS > 400 before trusting results")
print("- Our engine uses draws=2000, tune=1000, chains=2 — a good balance")