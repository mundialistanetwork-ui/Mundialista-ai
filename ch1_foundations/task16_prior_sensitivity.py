"""
Task 16: Prior Sensitivity Analysis
====================================
"""
import pymc as pm
import numpy as np
import arviz as az
import matplotlib.pyplot as plt

observed = np.array([1, 2, 1, 0, 3, 2, 1])

prior_configs = [
    {"name": "Informative (μ=1.3, σ=0.3)", "mu": 1.3, "sigma": 0.3},
    {"name": "Moderate (μ=1.3, σ=0.5)",    "mu": 1.3, "sigma": 0.5},
    {"name": "Vague (μ=1.3, σ=1.5)",       "mu": 1.3, "sigma": 1.5},
    {"name": "Wrong center (μ=3.0, σ=0.5)","mu": 3.0, "sigma": 0.5},
    {"name": "Very wrong (μ=0.1, σ=0.3)",  "mu": 0.1, "sigma": 0.3},
]

# ── PART A: Run PyMC for each prior configuration ──────────────
results = []
posterior_samples = {}

for config in prior_configs:
    print(f"\nRunning: {config['name']}...")
    with pm.Model():
        lam = pm.TruncatedNormal("lam", mu=config["mu"],
                                  sigma=config["sigma"],
                                  lower=0.05, upper=6.0)
        obs = pm.Poisson("obs", mu=lam, observed=observed)
        trace = pm.sample(draws=2000, tune=1000, chains=2,
                          cores=1, random_seed=42,
                          return_inferencedata=True,
                          progressbar=False)
    
    samples = trace.posterior["lam"].values.flatten()
    summary = az.summary(trace, var_names=["lam"])
    hdi = az.hdi(trace, var_names=["lam"], hdi_prob=0.94)
    hdi_vals = hdi["lam"].values
    
    results.append({
        "name": config["name"],
        "mean": samples.mean(),
        "hdi_low": hdi_vals[0],
        "hdi_high": hdi_vals[1],
    })
    posterior_samples[config["name"]] = samples

# ── PART B: Summary table ──────────────────────────────────────
print("\n=== PRIOR SENSITIVITY RESULTS ===")
print(f"{'Prior':<35} {'Post Mean':<12} {'94% HDI Low':<13} {'94% HDI High'}")
print("-" * 73)
for r in results:
    print(f"{r['name']:<35} {r['mean']:<12.3f} {r['hdi_low']:<13.3f} {r['hdi_high']:.3f}")
print(f"\nData mean: {observed.mean():.3f}")

# ── PART C: Overlay all posteriors ──────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
colors = ["blue", "green", "orange", "red", "purple"]

for (name, samples), color in zip(posterior_samples.items(), colors):
    ax.hist(samples, bins=50, alpha=0.4, color=color, label=name,
            density=True)

ax.axvline(x=observed.mean(), color="black", linestyle="--",
           linewidth=2, label=f"Data mean ({observed.mean():.2f})")
ax.set_xlabel("λ (goals per match)", fontsize=12)
ax.set_ylabel("Density", fontsize=12)
ax.set_title("Prior Sensitivity: How Prior Choice Affects the Posterior",
             fontsize=14)
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig("task16_sensitivity.png", dpi=150)
plt.show()
print("Saved: task16_sensitivity.png")

# ── PART D: Analysis ────────────────────────────────────────────
print("\n=== ANALYSIS ===")
print("1. The 'Informative' and 'Moderate' priors (both centered at 1.3)")
print("   produce posterior means closest to the data mean of 1.43,")
print("   since their prior centers are already near the truth.")
print("2. The 'Very wrong' prior (μ=0.1) still produces a reasonable")
print("   posterior because the data pulls it toward the truth.")
print("   However, with only 7 observations, it may not fully recover.")
print("3. With only 7 observations, the model is SOMEWHAT prior-sensitive.")
print("   Wrong priors do affect the posterior, but the data still has")
print("   a meaningful pull toward the truth.")
print("4. With 100 observations, the data would overwhelm ANY prior.")
print("   All five posteriors would converge to nearly the same value")
print("   — the data mean. More data = less prior sensitivity.")