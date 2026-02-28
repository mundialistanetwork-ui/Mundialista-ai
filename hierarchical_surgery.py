# hierarchical_surgery.py
# Run this with: python hierarchical_surgery.py

import re

file_path = "app.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# ── VERIFY line 304 has pm.Model ──
assert "with pm.Model" in lines[303], f"ERROR: Line 304 is: {lines[303]}"
print("Verified: pm.Model found at line 304")

# ── PART 1: Insert global means function before find_team_data (line 221) ──
global_mean_code = '''
# ────────────────────────────────────────────────────────────────────
# HIERARCHICAL PRIORS: Global mean across all teams (shrinkage target)
# ────────────────────────────────────────────────────────────────────
def _compute_global_means():
    """Compute global average attack/defense across all teams in database."""
    all_gf = []
    all_ga = []
    for team, data in TEAM_DATABASE.items():
        all_gf.append(data["avg_gf"])
        all_ga.append(data["avg_ga"])
    if len(all_gf) == 0:
        return {"global_attack": 1.2, "global_defense": 1.2}
    return {
        "global_attack": float(np.mean(all_gf)),
        "global_defense": float(np.mean(all_ga)),
    }

GLOBAL_MEANS = _compute_global_means()


'''

global_lines = global_mean_code.split('\n')
global_lines = [line + '\n' for line in global_lines]

# Insert before line 221 (index 220)
insert_at = 220
new_lines = lines[:insert_at] + global_lines + lines[insert_at:]

print(f"Inserted {len(global_lines)} lines at position {insert_at + 1}")

# ── PART 2: Find and replace the model block ──
# After insertion, everything shifted by len(global_lines)
shift = len(global_lines)

# Find the new position of "with pm.Model"
model_idx = None
for i, line in enumerate(new_lines):
    if "with pm.Model() as model:" in line:
        model_idx = i
        break

assert model_idx is not None, "ERROR: Could not find 'with pm.Model' after insertion"
print(f"Found pm.Model at new line {model_idx + 1}")

# Find the end of the 4 TruncatedNormal blocks (last "upper=6.0)")
end_idx = None
for i in range(model_idx, min(model_idx + 30, len(new_lines))):
    if "upper=6.0)" in new_lines[i]:
        end_idx = i
# end_idx is now the LAST line with "upper=6.0)"

assert end_idx is not None, "ERROR: Could not find end of TruncatedNormal block"
print(f"TruncatedNormal block ends at new line {end_idx + 1}")

# Build replacement
new_model_block = '''    with pm.Model() as model:
        # ── Hierarchical Priors (shrinkage toward global mean) ──
        SHRINKAGE_THRESHOLD = 30

        home_n = stats_home.get("n_matches", 1)
        away_n = stats_away.get("n_matches", 1)

        home_w = min(home_n / SHRINKAGE_THRESHOLD, 1.0)
        away_w = min(away_n / SHRINKAGE_THRESHOLD, 1.0)

        g_att = GLOBAL_MEANS["global_attack"]
        g_def = GLOBAL_MEANS["global_defense"]

        # Shrunk priors: blend team-specific with global mean
        home_att_mu = home_w * stats_home["avg_gf"] + (1 - home_w) * g_att
        home_def_mu = home_w * stats_home["avg_ga"] + (1 - home_w) * g_def
        away_att_mu = away_w * stats_away["avg_gf"] + (1 - away_w) * g_att
        away_def_mu = away_w * stats_away["avg_ga"] + (1 - away_w) * g_def

        # Sigma: less data = tighter prior (more shrinkage)
        home_sigma = 0.2 + (0.4 * home_w)
        away_sigma = 0.2 + (0.4 * away_w)

        home_attack = pm.TruncatedNormal(
            "home_attack", mu=home_att_mu,
            sigma=max(home_sigma, 0.3),
            lower=0.05, upper=6.0)
        home_defense = pm.TruncatedNormal(
            "home_defense", mu=home_def_mu,
            sigma=max(home_sigma, 0.3),
            lower=0.05, upper=6.0)
        away_attack = pm.TruncatedNormal(
            "away_attack", mu=away_att_mu,
            sigma=max(away_sigma, 0.3),
            lower=0.05, upper=6.0)
        away_defense = pm.TruncatedNormal(
            "away_defense", mu=away_def_mu,
            sigma=max(away_sigma, 0.3),
            lower=0.05, upper=6.0)
'''

replacement_lines = [line + '\n' for line in new_model_block.split('\n')]

# Replace from model_idx to end_idx (inclusive)
final_lines = new_lines[:model_idx] + replacement_lines + new_lines[end_idx + 1:]

# ── WRITE ──
with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(final_lines)

print(f"\nFinal file: {len(final_lines)} lines")
print("HIERARCHICAL PRIORS INSTALLED SUCCESSFULLY!")

# ── VALIDATE ──
import ast
try:
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    ast.parse(source)
    print("SYNTAX CHECK: OK ✓")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    print("Restoring backup...")
    import shutil
    shutil.copy("app_backup_before_hierarchical.py", file_path)
    print("Backup restored.")
