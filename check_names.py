"""Quick check: team name consistency between CSV and TEAM_DATABASE"""
from data_loader import load_results, get_all_teams

results = load_results(4)
teams = get_all_teams(results)
print(f"Total teams in CSV (last 4 years): {len(teams)}")
print(f"Matches loaded: {len(results)}")
print(f"Date range: {results.date.min().date()} to {results.date.max().date()}")
print()

# Names most likely to mismatch
db_teams = [
    "France", "Spain", "Germany", "England", "Brazil", "Argentina",
    "USA", "Mexico", "Japan", "South Korea", "Morocco",
    "Ivory Coast", "DR Congo", "Republic of Ireland",
    "Czech Republic", "Bosnia", "Trinidad and Tobago",
    "New Zealand", "New Caledonia", "UAE", "North Macedonia",
]

print("=== Name Check ===")
for t in db_teams:
    found = t in teams
    status = "YES" if found else "NOT FOUND"
    print(f"  {t}: {status}")

print()
print("=== First 30 Teams in CSV ===")
for t in sorted(teams)[:30]:
    print(f"  {t}")

print()
print("=== Last 30 Teams in CSV ===")
for t in sorted(teams)[-30:]:
    print(f"  {t}")