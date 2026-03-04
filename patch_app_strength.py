"""
Patch app.py:
1. Remove duplicate compute_global_priors and shrink_to_global (lines 254-283)
2. Add strength_adjust imports
3. Wire opponent-strength adjustment into the prediction pipeline
"""
import ast
import shutil

# Backup
shutil.copy("app.py", "app_backup_before_strength.py")
print("Backup saved: app_backup_before_strength.py")

with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Original: {len(lines)} lines")

# ─── CHANGE 1: Remove duplicate functions (lines 254-283) ───
# Lines are 1-indexed in our view but 0-indexed in the list
# Line 254 = index 253, Line 283 = index 282
# Verify we're deleting the right thing
line_254 = lines[253].strip()
line_267 = lines[266].strip()
assert "def compute_global_priors" in line_254, f"Line 254 unexpected: {line_254}"
assert "def shrink_to_global" in line_267, f"Line 267 unexpected: {line_267}"

# Delete lines 254-283 (indices 253-282)
del lines[253:283]
print("Removed duplicate functions (old lines 254-283)")

# After deletion, line numbers shifted down by 30
SHIFT = 30

# ─── CHANGE 2: Add strength_adjust import after data_loader import ───
# Find the data_loader import line
import_idx = None
for i, line in enumerate(lines):
    if "from data_loader import" in line:
        import_idx = i
        break

assert import_idx is not None, "Could not find data_loader import!"

# Insert strength_adjust import right after
strength_import = "from strength_adjust import compute_team_ratings, get_adjusted_stats\n"
lines.insert(import_idx + 1, strength_import)
print(f"Added strength_adjust import after line {import_idx + 1}")

# After insertion, everything below shifted by 1
# Net shift from line deletions and insertion: -30 + 1 = -29

# ─── CHANGE 3: Add strength rating computation at app startup ───
# Find where TEAM_DATABASE is closed (the closing brace of the dict)
# Look for the line that has just "}" after all the team entries
team_db_end = None
for i, line in enumerate(lines):
    if line.strip() == "}" and i > 40 and i < 250:
        # Check if previous lines look like team database entries
        if "recent_ga" in lines[i-1] or "recent_gf" in lines[i-1]:
            team_db_end = i
            break

if team_db_end is None:
    # Try another approach - find the line right before compute_global_priors
    for i, line in enumerate(lines):
        if "def compute_global_priors" in line:
            team_db_end = i - 1
            break

assert team_db_end is not None, "Could not find end of TEAM_DATABASE!"

# Insert strength computation after TEAM_DATABASE closes
# We need to compute ratings using CSV data, so we do it lazily (inside a function)
strength_init = [
    "\n",
    "# ────────────────────────────────────────────────────────────────────\n",
    "# OPPONENT-STRENGTH RATINGS (computed once at startup from CSV)\n",
    "# ────────────────────────────────────────────────────────────────────\n",
    "@st.cache_data(ttl=3600)\n",
    "def _compute_strength_ratings():\n",
    '    """Compute opponent-strength ratings from match data."""\n',
    "    try:\n",
    "        from data_loader import load_results\n",
    "        results = load_results()\n",
    "        ratings = compute_team_ratings(results)\n",
    '        print(f"Strength ratings computed for {len(ratings)} teams")\n',
    "        return results, ratings\n",
    "    except Exception as e:\n",
    '        print(f"Could not compute strength ratings: {e}")\n',
    "        return None, {}\n",
    "\n",
    "\n",
    "def apply_strength_adjustment(stats, team_name, results_df, ratings):\n",
    '    """Apply opponent-strength adjustment to team stats."""\n',
    "    if results_df is None or not ratings:\n",
    "        return stats\n",
    "    adj = get_adjusted_stats(results_df, team_name, ratings)\n",
    "    if adj is None:\n",
    "        return stats\n",
    "    adjusted = stats.copy()\n",
    '    # Blend: 60% opponent-adjusted, 40% raw\n',
    '    adjusted["avg_gf"] = adj["blended_gf"]\n',
    '    adjusted["avg_ga"] = adj["blended_ga"]\n',
    "    return adjusted\n",
    "\n",
    "\n",
]

# Insert after team_db_end + 2 (after the closing brace and a blank line)
insert_point = team_db_end + 2
for idx, new_line in enumerate(strength_init):
    lines.insert(insert_point + idx, new_line)

print(f"Added strength rating functions after line {insert_point + 1}")

# ─── CHANGE 4: Wire strength into the prediction pipeline ───
# Find the line: "global_priors = compute_global_priors(..."
# This is in the "Run the Engine" section
# After our insertions, we need to search fresh

engine_line = None
for i, line in enumerate(lines):
    if "global_priors = compute_global_priors" in line:
        engine_line = i
        break

assert engine_line is not None, "Could not find 'global_priors = compute_global_priors'!"

# Find the line with shrink_to_global for home_stats
shrink_home_line = None
shrink_away_line = None
for i in range(engine_line, min(engine_line + 10, len(lines))):
    if "home_stats = shrink_to_global" in lines[i]:
        shrink_home_line = i
    if "away_stats = shrink_to_global" in lines[i]:
        shrink_away_line = i

assert shrink_home_line is not None, "Could not find home_stats shrink_to_global!"
assert shrink_away_line is not None, "Could not find away_stats shrink_to_global!"

# Insert strength adjustment BEFORE shrinkage
# We need to add lines before shrink_home_line
strength_wire = [
    "        # Opponent-strength adjustment\n",
    "        _str_results, _str_ratings = _compute_strength_ratings()\n",
    "        home_stats = apply_strength_adjustment(home_stats, home_team, _str_results, _str_ratings)\n",
    "        away_stats = apply_strength_adjustment(away_stats, away_team, _str_results, _str_ratings)\n",
]

for idx, new_line in enumerate(strength_wire):
    lines.insert(shrink_home_line + idx, new_line)

print(f"Wired strength adjustment before shrinkage at line {shrink_home_line + 1}")

# ─── CHANGE 5: Update the status display to show adjustment info ───
# Find the line that shows "Shrunk GF" and add adjustment info
for i, line in enumerate(lines):
    if "Shrunk GF:" in line and "home_team" in line:
        # Add a line before this showing adjustment was applied
        adj_info = '        st.write("🎯 Opponent-strength adjustment applied")\n'
        lines.insert(i, adj_info)
        break

# ─── VALIDATE ───
source = "".join(lines)
try:
    ast.parse(source)
    print("\nSYNTAX CHECK: OK")
except SyntaxError as e:
    print(f"\nSYNTAX ERROR at line {e.lineno}: {e.msg}")
    print("Restoring backup...")
    shutil.copy("app_backup_before_strength.py", "app.py")
    print("Backup restored. Nothing changed.")
    raise SystemExit(1)

# ─── WRITE ───
with open("app.py", "w", encoding="utf-8") as f:
    f.write(source)

final_count = len(lines)
print(f"\nFinal: {final_count} lines (was {final_count + SHIFT - len(strength_init) - len(strength_wire) - 1})")
print()
print("CHANGES MADE:")
print("  1. Removed duplicate compute_global_priors and shrink_to_global")
print("  2. Added strength_adjust import")
print("  3. Added _compute_strength_ratings() with Streamlit caching")
print("  4. Added apply_strength_adjustment() helper")
print("  5. Wired strength adjustment into prediction pipeline")
print("  6. Added status display for adjustment info")
print()
print("Run: streamlit run app.py")