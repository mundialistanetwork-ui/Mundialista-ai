import re

with open("app.py", "r", encoding="utf-8") as f:
    src = f.read()

shrinkage_code = '''
def compute_global_priors(results_df=None):
    """Compute global average attack/defense across all known teams."""
    if results_df is not None:
        avg_gf = results_df.groupby("home_team")["home_score"].mean().mean()
        avg_ga = results_df.groupby("home_team")["away_score"].mean().mean()
    else:
        all_gf = [v["avg_gf"] for v in TEAM_DATABASE.values()]
        all_ga = [v["avg_ga"] for v in TEAM_DATABASE.values()]
        avg_gf = np.mean(all_gf)
        avg_ga = np.mean(all_ga)
    return {"global_gf": avg_gf, "global_ga": avg_ga}


def shrink_to_global(stats, global_priors, shrink_k=8):
    """
    Bayesian shrinkage toward global mean.
    Teams with fewer matches get pulled harder toward the average.
    shrink_k=8: Mexico (n=40) barely moves, Iceland/Bhutan (n=5) pulled ~60% toward mean.
    """
    n = stats["n_matches"]
    g_gf = global_priors["global_gf"]
    g_ga  = global_priors["global_ga"]
    blended_gf = (n * stats["avg_gf"] + shrink_k * g_gf) / (n + shrink_k)
    blended_ga = (n * stats["avg_ga"] + shrink_k * g_ga) / (n + shrink_k)
    shrunk = stats.copy()
    shrunk["avg_gf"] = blended_gf
    shrunk["avg_ga"] = blended_ga
    shrunk["std_gf"] = stats["std_gf"] * (n / (n + shrink_k)) + 0.3 * (shrink_k / (n + shrink_k))
    shrunk["std_ga"] = stats["std_ga"] * (n / (n + shrink_k)) + 0.3 * (shrink_k / (n + shrink_k))
    return shrunk

'''

anchor1 = "def find_team_data(team_name: str)"
if anchor1 in src:
    src = src.replace(anchor1, shrinkage_code + anchor1)
    print("PATCH 1 OK: shrinkage functions inserted")
else:
    print("PATCH 1 FAILED: could not find find_team_data")

old_status = '    with st.status("\U0001f4ca Computing team statistics\u2026", expanded=False):\n        st.write(f"**{home_team}** \u2014 Avg GF: {home_stats[\'avg_gf\']:.2f}, Avg GA: {home_stats[\'avg_ga\']:.2f}")\n        st.write(f"**{away_team}** \u2014 Avg GF: {away_stats[\'avg_gf\']:.2f}, Avg GA: {away_stats[\'avg_ga\']:.2f}")'

new_status = '    with st.status("\U0001f4ca Computing team statistics\u2026", expanded=False):\n        global_priors = compute_global_priors(csv_results if use_csv else None)\n        home_stats = shrink_to_global(home_stats, global_priors)\n        away_stats = shrink_to_global(away_stats, global_priors)\n        st.write(f"**{home_team}** \u2014 Shrunk GF: {home_stats[\'avg_gf\']:.2f}, Shrunk GA: {home_stats[\'avg_ga\']:.2f}")\n        st.write(f"**{away_team}** \u2014 Shrunk GF: {away_stats[\'avg_gf\']:.2f}, Shrunk GA: {away_stats[\'avg_ga\']:.2f}")\n        st.caption(f"\U0001f30d Global baseline: {global_priors[\'global_gf\']:.2f} GF / {global_priors[\'global_ga\']:.2f} GA (shrink_k=8)")'

if old_status in src:
    src = src.replace(old_status, new_status)
    print("PATCH 2 OK: shrinkage applied before inference")
else:
    print("PATCH 2 FAILED: trying fallback search...")
    # Fallback: search line by line
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if 'Computing team statistics' in line and 'st.status' in line:
            print(f"  Found status block at line {i+1}: {line.strip()}")
            break

with open("app.py", "w", encoding="utf-8") as f:
    f.write(src)

import ast
try:
    ast.parse(src)
    print("Syntax OK - app.py is valid Python")
except SyntaxError as e:
    print(f"Syntax ERROR: {e}")
