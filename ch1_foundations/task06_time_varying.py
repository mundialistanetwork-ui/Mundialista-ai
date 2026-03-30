"""
Task 06: Visualizing Time-Varying Goal Intensity
=================================================
"""
import numpy as np
import matplotlib.pyplot as plt

# ── PART A: Define two intensity profiles ───────────────────────
base_rate = 1.3
minutes = np.arange(90)

# FLAT profile
flat_profile = np.full(90, base_rate / 90)

# VARIABLE profile
multipliers = np.ones(90)
multipliers[0:15] = 0.85
multipliers[15:45] = 1.00
multipliers[45:60] = 1.10
multipliers[60:80] = 1.05
multipliers[80:90] = 1.30

variable_profile = np.full(90, base_rate / 90) * multipliers
variable_profile = variable_profile * (base_rate / variable_profile.sum())

# ── PART B: Plot both profiles ──────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(minutes, flat_profile, label="Flat Profile", color="blue",
        linewidth=2, linestyle="--")
ax.step(minutes, variable_profile, label="Variable Profile",
        color="red", linewidth=2, where="mid")
ax.axvline(x=45, color="gray", linestyle=":", label="Half-time")
ax.axvline(x=80, color="orange", linestyle=":", label="Final push (min 80)")
ax.set_xlabel("Minute", fontsize=12)
ax.set_ylabel("λ(t) per minute", fontsize=12)
ax.set_title("Goal Intensity Profiles: Flat vs Time-Varying", fontsize=14)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("task06_intensity_profiles.png", dpi=150)
plt.show()
print("Saved: task06_intensity_profiles.png")

# ── PART C: Verify normalization ───────────────────────────────
print(f"\nFlat profile sum: {flat_profile.sum():.4f}")
print(f"Variable profile sum: {variable_profile.sum():.4f}")
print(f"Both equal 1.3? Flat={'✅' if abs(flat_profile.sum()-1.3)<0.001 else '❌'}, "
      f"Variable={'✅' if abs(variable_profile.sum()-1.3)<0.001 else '❌'}")

# ── PART D: Cumulative intensity ───────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(minutes, np.cumsum(flat_profile), label="Flat (cumulative)",
        color="blue", linewidth=2, linestyle="--")
ax.plot(minutes, np.cumsum(variable_profile),
        label="Variable (cumulative)", color="red", linewidth=2)
ax.axhline(y=1.3, color="gray", linestyle=":", alpha=0.5)
ax.axvline(x=45, color="gray", linestyle=":", alpha=0.5)
ax.set_xlabel("Minute", fontsize=12)
ax.set_ylabel("Cumulative Expected Goals", fontsize=12)
ax.set_title("Cumulative Goal Intensity Over 90 Minutes", fontsize=14)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("task06_cumulative_intensity.png", dpi=150)
plt.show()
print("Saved: task06_cumulative_intensity.png")