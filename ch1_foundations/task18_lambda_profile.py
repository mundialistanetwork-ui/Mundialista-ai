"""
Task 18: Production-Quality Lambda Profile
==========================================
"""
import numpy as np
import matplotlib.pyplot as plt

# ── PART A: Implement lambda_profile ────────────────────────────
# Precompute normalization factor
_MULTIPLIERS = np.ones(90)
_MULTIPLIERS[0:15] = 0.85
_MULTIPLIERS[15:45] = 1.00
_MULTIPLIERS[45:60] = 1.10
_MULTIPLIERS[60:80] = 1.05
_MULTIPLIERS[80:90] = 1.30
_NORM_FACTOR = _MULTIPLIERS.sum() / 90.0

def lambda_profile(base_rate: float, minute: int) -> float:
    """
    Return the instantaneous Poisson rate for a single minute.
    
    Parameters
    ----------
    base_rate : float — total expected goals for 90 minutes
    minute    : int   — match minute (0-89)
    
    Returns
    -------
    float — the rate for that minute, normalized so sum over
            90 minutes equals base_rate
    """
    if base_rate <= 0:
        return 0.0
    if minute < 0 or minute >= 90:
        return 0.0
    
    return (base_rate / 90.0) * _MULTIPLIERS[minute] / _NORM_FACTOR


# ── PART B: Verification test suite ────────────────────────────
def run_tests():
    print("=== RUNNING TESTS ===")
    
    # Test 1: Sum over 90 minutes equals base_rate
    for rate in [0.5, 1.0, 1.3, 2.5, 4.0]:
        total = sum(lambda_profile(rate, m) for m in range(90))
        passed = abs(total - rate) < 1e-10
        print(f"  Test 1 (rate={rate}): sum={total:.10f} "
              f"{'✅' if passed else '❌'}")
    
    # Test 2: Minutes 80-89 have higher rates than 15-44
    rate_80 = lambda_profile(1.3, 85)
    rate_30 = lambda_profile(1.3, 30)
    passed = rate_80 > rate_30
    print(f"  Test 2: min85 ({rate_80:.6f}) > min30 ({rate_30:.6f}) "
          f"{'✅' if passed else '❌'}")
    
    # Test 3: base_rate=0 returns 0
    passed = lambda_profile(0, 45) == 0.0
    print(f"  Test 3: rate=0 gives 0 {'✅' if passed else '❌'}")
    
    # Test 4: Out of range minutes return 0
    passed = lambda_profile(1.3, -1) == 0.0 and lambda_profile(1.3, 90) == 0.0
    print(f"  Test 4: out-of-range minutes give 0 {'✅' if passed else '❌'}")
    
    print("All tests complete!")

run_tests()

# ── PART C: Comparative visualization ──────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
minutes = np.arange(90)

for rate, color, label in [(0.8, "blue", "Weak (λ=0.8)"),
                            (1.3, "green", "Average (λ=1.3)"),
                            (2.5, "red", "Strong (λ=2.5)")]:
    profile = [lambda_profile(rate, m) for m in minutes]
    ax.step(minutes, profile, color=color, linewidth=2,
            label=label, where="mid")

ax.set_xlabel("Minute", fontsize=12)
ax.set_ylabel("λ(t) per minute", fontsize=12)
ax.set_title("Lambda Profile for Different Team Strengths", fontsize=14)
ax.axvline(x=45, color="gray", linestyle=":", alpha=0.5)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("task18_lambda_profiles.png", dpi=150)
plt.show()
print("Saved: task18_lambda_profiles.png")

# ── PART D: Alternative profiles ───────────────────────────────
def lambda_flat(base_rate, minute):
    """Flat profile — constant every minute."""
    if base_rate <= 0 or minute < 0 or minute >= 90:
        return 0.0
    return base_rate / 90.0

def lambda_aggressive(base_rate, minute):
    """Aggressive — very low 1st half, very high 2nd half."""
    if base_rate <= 0 or minute < 0 or minute >= 90:
        return 0.0
    mult = np.ones(90)
    mult[0:45] = 0.6
    mult[45:75] = 1.2
    mult[75:90] = 1.8
    norm = mult.sum() / 90.0
    return (base_rate / 90.0) * mult[minute] / norm

fig, ax = plt.subplots(figsize=(12, 5))

for func, color, label in [(lambda_profile, "green", "Standard"),
                             (lambda_flat, "blue", "Flat"),
                             (lambda_aggressive, "red", "Aggressive")]:
    profile = [func(1.3, m) for m in minutes]
    ax.step(minutes, profile, color=color, linewidth=2,
            label=label, where="mid")

ax.set_xlabel("Minute", fontsize=12)
ax.set_ylabel("λ(t) per minute", fontsize=12)
ax.set_title("Profile Comparison (all base_rate=1.3)", fontsize=14)
ax.axvline(x=45, color="gray", linestyle=":", alpha=0.5)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("task18_profile_comparison.png", dpi=150)
plt.show()
print("Saved: task18_profile_comparison.png")

# Verify all sum to 1.3
for name, func in [("Standard", lambda_profile),
                    ("Flat", lambda_flat),
                    ("Aggressive", lambda_aggressive)]:
    total = sum(func(1.3, m) for m in range(90))
    print(f"  {name} sum: {total:.6f} {'✅' if abs(total-1.3)<0.001 else '❌'}")