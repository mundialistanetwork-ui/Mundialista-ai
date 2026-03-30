"""
Task 13: Two-Team Bayesian Strength Estimation
===============================================
"""
import pymc as pm
import numpy as np
import arviz as az
import matplotlib.pyplot as plt

# ── DATA ────────────────────────────────────────────────────────
jamaica_gf = np.array([1, 0, 2, 1, 0, 3, 2])
jamaica_ga = np.array([0, 1, 1, 1, 2, 0, 0])

newcal_gf = np.array([1, 0, 2, 1, 0, 1, 3])
newcal_ga = np.array([1, 2, 1, 0, 4, 1, 0])

# ── PART A: Summary statistics ──────────────────────────────────
stats = {
    "Jamaica": {
        "avg_gf": jamaica_gf.mean(), "avg_ga": jamaica_ga.mean(),
        "std_gf": jamaica_gf.std(), "std_ga": jamaica_ga.std(),
    },
    "New Caledonia": {
        "avg_gf": newcal_gf.mean(), "avg_ga": newcal_ga.mean(),
        "std_gf": newcal_gf.std(), "std_ga": newcal_ga.std(),
    },
}

print("=== TEAM STATISTICS ===")
for team, s in stats.items():
    print(f"\n{team}:")
    for key, val in s.items():
        print(f"  {key}: {val:.3f}")

# ── PART B: Build the PyMC model ───────────────────────────────
with pm.Model() as two_team_model:
    home_attack = pm.TruncatedNormal(
        "home_attack", mu=stats["Jamaica"]["avg_gf"],
        sigma=max(stats["Jamaica"]["std_gf"], 0.3),
        lower=0.05, upper=6.0)
    
    home_defense = pm.TruncatedNormal(
        "home_defense", mu=stats["Jamaica"]["avg_ga"],
        sigma=max(stats["Jamaica"]["std_ga"], 0.3),
        lower=0.05, upper=6.0)
    
    away_attack = pm.TruncatedNormal(
        "away_attack", mu=stats["New Caledonia"]["avg_gf"],
        sigma=max(stats["New Caledonia"]["std_gf"], 0.3),
        lower=0.05, upper=6.0)
    
    away_defense = pm.TruncatedNormal(
        "away_defense", mu=stats["New Caledonia"]["avg_ga"],
        sigma=max(stats["New Caledonia"]["std_ga"], 0.3),
        lower=0.05, upper=6.0)
    
    # Likelihoods
    jamaica_scored = pm.Poisson("jamaica_scored", mu=home_attack,
                                 observed=jamaica_gf)
    jamaica_conceded = pm.Poisson("jamaica_conceded", mu=home_defense,
                                   observed=jamaica_ga)
    newcal_scored = pm.Poisson("newcal_scored", mu=away_attack,
                                observed=newcal_gf)
    newcal_conceded = pm.Poisson("newcal_conceded", mu=away_defense,
                                  observed=newcal_ga)

# ── PART C: Sample ─────────────────────────────────────────────
print("\nSampling... (this may take a few minutes)")
with two_team_model:
    trace = pm.sample(
        draws=2000, tune=1000, chains=2, cores=1,
        random_seed=42, return_inferencedata=True,
        progressbar=True,
    )

# ── PART D: Print summary and plot posteriors ───────────────────
print("\n=== POSTERIOR SUMMARY ===")
print(az.summary(trace, var_names=["home_attack", "home_defense",
                                    "away_attack", "away_defense"]))

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
params = ["home_attack", "home_defense", "away_attack", "away_defense"]
titles = ["Jamaica Attack", "Jamaica Defense", 
          "New Caledonia Attack", "New Caledonia Defense"]

for ax, param, title in zip(axes.flatten(), params, titles):
    samples = trace.posterior[param].values.flatten()
    ax.hist(samples, bins=50, color="steelblue", edgecolor="black", alpha=0.7)
    ax.axvline(samples.mean(), color="red", linestyle="--",
               label=f"Mean: {samples.mean():.3f}")
    ax.set_title(title)
    ax.legend()

plt.tight_layout()
plt.savefig("task13_two_team_posteriors.png", dpi=150)
plt.show()
print("Saved: task13_two_team_posteriors.png")

# ── PART E: How would we use these posteriors? ──────────────────
print("\n=== FIRST 10 PARAMETER DRAWS ===")
ha = trace.posterior["home_attack"].values.flatten()
hd = trace.posterior["home_defense"].values.flatten()
aa = trace.posterior["away_attack"].values.flatten()
ad = trace.posterior["away_defense"].values.flatten()

print(f"{'#':<4} {'Home Atk':<10} {'Home Def':<10} {'Away Atk':<10} {'Away Def':<10}")
print("-" * 44)
for i in range(10):
    print(f"{i+1:<4} {ha[i]:<10.3f} {hd[i]:<10.3f} {aa[i]:<10.3f} {ad[i]:<10.3f}")

print("\nFor each simulation, we'd combine these into match rates:")
print("  Jamaica's rate = f(home_attack, away_defense)")
print("  New Caledonia's rate = f(away_attack, home_defense)")
