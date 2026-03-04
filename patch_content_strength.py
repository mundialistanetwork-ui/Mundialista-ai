"""
Patch content_automation.py to use opponent-strength-adjusted stats
"""
import ast

with open("content_automation.py", "r", encoding="utf-8") as f:
    source = f.read()

# We need to replace the quick_simulate function's stat calculation
# Currently it uses raw stats + simple shrinkage
# We'll add strength adjustment

old_simulate_start = "def quick_simulate(home_team, away_team, n_sims=10200):"
assert old_simulate_start in source, "Could not find quick_simulate!"

new_simulate = '''def quick_simulate(home_team, away_team, n_sims=10200):
    home_stats = get_team_stats(RESULTS_DF, home_team)
    away_stats = get_team_stats(RESULTS_DF, away_team)
    if home_stats is None:
        home_stats = {"avg_gf": GLOBAL_GF, "avg_ga": GLOBAL_GA, "n_matches": 1}
    if away_stats is None:
        away_stats = {"avg_gf": GLOBAL_GF, "avg_ga": GLOBAL_GA, "n_matches": 1}
    # Opponent-strength adjustment
    h_adj = get_adjusted_stats(RESULTS_DF, home_team, TEAM_RATINGS)
    a_adj = get_adjusted_stats(RESULTS_DF, away_team, TEAM_RATINGS)
    if h_adj is not None:
        home_stats["avg_gf"] = h_adj["blended_gf"]
        home_stats["avg_ga"] = h_adj["blended_ga"]
    if a_adj is not None:
        away_stats["avg_gf"] = a_adj["blended_gf"]
        away_stats["avg_ga"] = a_adj["blended_ga"]
    # Shrinkage toward global mean
    shrink_k = 8
    h_n = home_stats["n_matches"]
    a_n = away_stats["n_matches"]
    h_gf = (h_n * home_stats["avg_gf"] + shrink_k * GLOBAL_GF) / (h_n + shrink_k)
    h_ga = (h_n * home_stats["avg_ga"] + shrink_k * GLOBAL_GA) / (h_n + shrink_k)
    a_gf = (a_n * away_stats["avg_gf"] + shrink_k * GLOBAL_GF) / (a_n + shrink_k)
    a_ga = (a_n * away_stats["avg_ga"] + shrink_k * GLOBAL_GA) / (a_n + shrink_k)
    home_lambda = max(0.3, h_gf * (a_ga / GLOBAL_GA) * 1.05)
    away_lambda = max(0.3, a_gf * (h_ga / GLOBAL_GA) * 0.95)
    rng = np.random.default_rng(42)
    home_goals = rng.poisson(home_lambda, n_sims)
    away_goals = rng.poisson(away_lambda, n_sims)
    home_wins = int(np.sum(home_goals > away_goals))
    draws = int(np.sum(home_goals == away_goals))
    away_wins = int(np.sum(home_goals < away_goals))
    scorelines = list(zip(home_goals.tolist(), away_goals.tolist()))
    score_counts = Counter(scorelines)
    top5 = score_counts.most_common(5)
    if home_lambda >= away_lambda:
        favourite, underdog = home_team, away_team
        upset_prob = away_wins / n_sims * 100
    else:
        favourite, underdog = away_team, home_team
        upset_prob = home_wins / n_sims * 100
    return {"home_win_pct": home_wins / n_sims * 100,
            "draw_pct": draws / n_sims * 100,
            "away_win_pct": away_wins / n_sims * 100,
            "home_exp": float(np.mean(home_goals)),
            "away_exp": float(np.mean(away_goals)),
            "home_lambda": home_lambda,
            "away_lambda": away_lambda,
            "top5_scorelines": top5,
            "upset_prob": upset_prob,
            "favourite": favourite,
            "underdog": underdog,
            "n": n_sims,
            "home_n_matches": home_stats["n_matches"],
            "away_n_matches": away_stats["n_matches"]}'''

# Find the old function and its end
old_start_idx = source.index(old_simulate_start)
# Find the next "def " after quick_simulate
rest = source[old_start_idx + len(old_simulate_start):]
next_def_pos = rest.index("\ndef ")
old_end_idx = old_start_idx + len(old_simulate_start) + next_def_pos

old_function = source[old_start_idx:old_end_idx]

# Replace
source = source[:old_start_idx] + new_simulate + source[old_end_idx:]

# Now add imports and TEAM_RATINGS computation after the GLOBAL_GA line
# Find where GLOBAL_GA is set
ga_line = 'print(f"Global baseline: {GLOBAL_GF:.2f} GF / {GLOBAL_GA:.2f} GA")'
assert ga_line in source, "Could not find GLOBAL_GA print line!"

strength_code = '''

# Opponent-strength ratings
from strength_adjust import compute_team_ratings, get_adjusted_stats
print("Computing opponent-strength ratings...")
TEAM_RATINGS = compute_team_ratings(RESULTS_DF)
print(f"Ratings computed for {len(TEAM_RATINGS)} teams")
'''

source = source.replace(ga_line, ga_line + strength_code)

# Validate
try:
    ast.parse(source)
    print("SYNTAX CHECK: OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")
    print("NOT writing. Nothing changed.")
    raise SystemExit(1)

with open("content_automation.py", "w", encoding="utf-8") as f:
    f.write(source)

print("content_automation.py PATCHED with opponent-strength adjustment!")
print("Run: python content_automation.py")