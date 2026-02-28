import sys
sys.path.insert(0, ".")
from data_loader import load_results, get_team_stats_for_app, get_team_matches

results = load_results(years_lookback=4)

for team, opponent in [("Mexico", "Iceland"), ("Iceland", "Mexico")]:
    matches = get_team_matches(results, team)
    stats = get_team_stats_for_app(results, team, opponent)
    print(f"\n{'='*50}")
    print(f"  {team}")
    print(f"  Matches in CSV:  {len(matches)}")
    if stats:
        print(f"  avg_gf (raw):    {stats['avg_gf']:.3f}")
        print(f"  avg_ga (raw):    {stats['avg_ga']:.3f}")
        print(f"  n_matches:       {stats['n_matches']}")
        # Show shrinkage manually
        k = 8
        pull = k / (stats['n_matches'] + k) * 100
        print(f"  shrinkage pull:  {pull:.1f}% toward mean")
    else:
        print("  !! NO STATS FOUND !!")

# Also check if shrinkage functions exist in app.py
with open("app.py", "r", encoding="utf-8") as f:
    src = f.read()

print(f"\n{'='*50}")
print(f"  PATCH STATUS:")
print(f"  shrink_to_global in app.py:      {'YES' if 'shrink_to_global' in src else 'NO -- PATCH NEVER APPLIED'}")
print(f"  compute_global_priors in app.py: {'YES' if 'compute_global_priors' in src else 'NO -- PATCH NEVER APPLIED'}")
print(f"  shrinkage called in main():      {'YES' if 'home_stats = shrink_to_global' in src else 'NO -- PATCH 2 FAILED'}")
print(f"{'='*50}\n")
