print("Fixing home bias for top matchups...")

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

with open('content_automation_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)

# Find and replace the home advantage + convergence block
old_block = '''    # Close-match convergence: when teams are close, push lambdas together
    if rank_gap < 20:
        avg_lambda = (home_blend + away_blend) / 2
        converge = 0.15 * (1 - rank_gap / 20)
        home_blend = home_blend * (1 - converge) + avg_lambda * converge
        away_blend = away_blend * (1 - converge) + avg_lambda * converge
    # Apply star player impact
    home_star = get_team_star_impact(home_team)
    away_star = get_team_star_impact(away_team)
    home_blend *= home_star
    away_blend *= away_star
    # Apply home advantage
    home_lambda = max(0.3, home_blend * 1.08)
    away_lambda = max(0.3, away_blend * 0.92)'''

new_block = '''    # Close-match convergence: push close teams toward equal
    if rank_gap < 30:
        avg_lambda = (home_blend + away_blend) / 2
        converge = 0.25 * (1 - rank_gap / 30)  # up to 25% pull for same-rank teams
        home_blend = home_blend * (1 - converge) + avg_lambda * converge
        away_blend = away_blend * (1 - converge) + avg_lambda * converge
    # Apply star player impact
    home_star = get_team_star_impact(home_team)
    away_star = get_team_star_impact(away_team)
    home_blend *= home_star
    away_blend *= away_star
    # Apply home advantage (moderate - 4% boost)
    home_lambda = max(0.3, home_blend * 1.04)
    away_lambda = max(0.3, away_blend * 0.96)'''

if old_block in code:
    code = code.replace(old_block, new_block)
    print("Replaced! Changes:")
    print("  - Convergence: rank_gap < 20 -> < 30")
    print("  - Convergence strength: 15% -> 25%")
    print("  - Home advantage: 1.08/0.92 -> 1.04/0.96")
else:
    print("ERROR: Block not found!")
    exit()

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
import sys
for mod in list(sys.modules.keys()):
    if 'content' in mod or 'data_loader' in mod or 'strength' in mod or 'player' in mod:
        del sys.modules[mod]

from content_automation import quick_simulate

tests = [
    ('Argentina', 'Brazil', 'Close ~35/30/35'),
    ('Brazil', 'Argentina', 'Close ~35/30/35'),
    ('France', 'England', 'France slight ~36/30/34'),
    ('Spain', 'Germany', 'Close ~35/30/35'),
    ('Germany', 'United States', 'Germany edge ~40/28/32'),
    ('Bolivia', 'Suriname', 'Bolivia clear ~48/27/25'),
    ('Brazil', 'India', 'Brazil dom ~65/20/15'),
    ('Norway', 'San Marino', 'Crush ~80/12/8'),
    ('France', 'San Marino', 'Crush ~85/10/5'),
    ('Colombia', 'Peru', 'Close ~40/30/30'),
]

print(f"\n  {'Matchup':<30s} {'Home':>6s} {'Draw':>6s} {'Away':>6s}  Target")
print("  " + "-" * 80)
for home, away, note in tests:
    r = quick_simulate(home, away)
    hw = r['home_win_pct']
    d = r['draw_pct']
    aw = r['away_win_pct']
    print(f"  {home+' v '+away:<30s} {hw:5.1f}% {d:5.1f}% {aw:5.1f}%  ({note})")
