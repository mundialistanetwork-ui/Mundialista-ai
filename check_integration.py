"""Test the new get_team_stats_for_app function"""
from data_loader import load_results, get_team_stats_for_app, resolve_team_name, get_all_teams

results = load_results(4)
teams = get_all_teams(results)

print("=== Testing resolve_team_name ===")
for name in ["USA", "Bosnia", "UAE", "France", "brazil"]:
    resolved = resolve_team_name(name, teams)
    print(f"  {name} -> {resolved}")

print()
print("=== Testing get_team_stats_for_app ===")

# Test 1: Normal match
stats = get_team_stats_for_app(results, "Brazil", "Argentina")
if stats:
    print(f"  Brazil vs Argentina:")
    print(f"    avg_gf: {stats['avg_gf']:.2f}")
    print(f"    avg_ga: {stats['avg_ga']:.2f}")
    print(f"    std_gf: {stats['std_gf']:.2f}")
    print(f"    std_ga: {stats['std_ga']:.2f}")
    print(f"    n_matches: {stats['n_matches']}")
    print(f"    goals_for array: {stats['goals_for']}")
    print(f"    goals_against array: {stats['goals_against']}")
    print(f"    h2h_n: {stats['h2h_n']}")
    print(f"    found: {stats['found']}")
else:
    print("  ERROR: returned None!")

# Test 2: Alias match
print()
stats2 = get_team_stats_for_app(results, "USA", "Mexico")
if stats2:
    print(f"  USA vs Mexico:")
    print(f"    avg_gf: {stats2['avg_gf']:.2f}")
    print(f"    n_matches: {stats2['n_matches']}")
    print(f"    found: {stats2['found']}")
else:
    print("  ERROR: USA returned None!")

# Test 3: Unknown team
print()
stats3 = get_team_stats_for_app(results, "Atlantis", "Brazil")
print(f"  Atlantis vs Brazil: {stats3}")
print()
print("ALL TESTS PASSED!" if stats and stats2 and stats3 is None else "SOME TESTS FAILED")