with open("data_loader.py", "r", encoding="utf-8") as f:
    src = f.read()

old = "def get_team_stats_for_app(results, team, opponent, last_n=7):"
new = "def get_team_stats_for_app(results, team, opponent, last_n=40):"

if old in src:
    src = src.replace(old, new)
    print("PATCH OK: last_n changed from 7 to 40")
else:
    print("PATCH FAILED: could not find function signature")

old2 = "recent = team_matches.head(last_n)"
new2 = "recent = team_matches.head(last_n)  # uses last 40 matches for robust stats"

src = src.replace(old2, new2)

with open("data_loader.py", "w", encoding="utf-8") as f:
    f.write(src)

import ast
try:
    ast.parse(src)
    print("Syntax OK")
except SyntaxError as e:
    print(f"Syntax ERROR: {e}")
