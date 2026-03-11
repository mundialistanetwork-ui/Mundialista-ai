print("Fixing import...")

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Backup
with open('content_automation_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)

# Fix 1: last_n=40 to last_n=7
old_def = 'def get_team_stats(results, team, last_n=40):'
new_def = 'def get_team_stats(results, team, last_n=7):'
if old_def in code:
    code = code.replace(old_def, new_def)
    print("Changed last_n from 40 to 7")

# Fix 2: Add player_impact import on its own line
if 'from player_impact import' not in code:
    code = code.replace(
        'from data_loader import get_team_ranking',
        'from data_loader import get_team_ranking\nfrom player_impact import get_team_star_impact'
    )
    print("Added player_impact import")

# Fix 3: Add star player impact before home advantage
old_home = '    # Apply home advantage\n    home_lambda = max(0.3, home_blend * 1.08)\n    away_lambda = max(0.3, away_blend * 0.92)'

new_home = """    # Apply star player impact
    home_star = get_team_star_impact(home_team)
    away_star = get_team_star_impact(away_team)
    home_blend *= home_star
    away_blend *= away_star
    # Apply home advantage
    home_lambda = max(0.3, home_blend * 1.08)
    away_lambda = max(0.3, away_blend * 0.92)"""

if old_home in code:
    code = code.replace(old_home, new_home)
    print("Added star player impact")
elif '# Apply home advantage' in code:
    print("Home advantage block found but format different - doing line search...")
    lines = code.split('\n')
    new_lines = []
    inserted = False
    for i, line in enumerate(lines):
        if '# Apply home advantage' in line and not inserted:
            new_lines.append('    # Apply star player impact')
            new_lines.append('    home_star = get_team_star_impact(home_team)')
            new_lines.append('    away_star = get_team_star_impact(away_team)')
            new_lines.append('    home_blend *= home_star')
            new_lines.append('    away_blend *= away_star')
            inserted = True
        new_lines.append(line)
    if inserted:
        code = '\n'.join(new_lines)
        print("Added star player impact (line search method)")

with open('content_automation.py', 'w', encoding='utf-8') as f:
    f.write(code)

import py_compile
try:
    py_compile.compile('content_automation.py', doraise=True)
    print("\nSYNTAX CHECK: OK")
except py_compile.PyCompileError as e:
    print(f"\nSYNTAX ERROR: {e}")
    with open('content_automation_backup.py', 'r', encoding='utf-8') as f:
        backup = f.read()
    with open('content_automation.py', 'w', encoding='utf-8') as f:
        f.write(backup)
    print("Backup restored!")
    exit()

# Test
print("\nTesting...")
import sys
for mod in list(sys.modules.keys()):
    if 'content' in mod or 'data_loader' in mod or 'strength' in mod or 'player' in mod:
        del sys.modules[mod]

from content_automation import quick_simulate
from player_impact import get_team_star_impact

print("\nStar Impact:")
for team in ['Argentina', 'Norway', 'Bolivia']:
    print(f"  {team}: {get_team_star_impact(team):.2f}x")

print("\nPredictions:")
tests = [
    ('Argentina', 'Brazil'),
    ('France', 'England'),
    ('Bolivia', 'Suriname'),
    ('Brazil', 'India'),
    ('Norway', 'San Marino'),
]
for home, away in tests:
    r = quick_simulate(home, away)
    print(f"  {home} {r['home_win_pct']:.1f}% | Draw {r['draw_pct']:.1f}% | {away} {r['away_win_pct']:.1f}%")

print("\nAll upgrades working!")
