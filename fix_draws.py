print("Fine-tuning draws + mismatch protection...")

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

with open('content_automation_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)

old_block = '''    # Close-match convergence: push close teams toward equal
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

new_block = '''    # Close-match convergence: push close teams toward equal
    if rank_gap < 40:
        avg_lambda = (home_blend + away_blend) / 2
        converge = 0.30 * (1 - rank_gap / 40)
        home_blend = home_blend * (1 - converge) + avg_lambda * converge
        away_blend = away_blend * (1 - converge) + avg_lambda * converge
    # Draw boost: push lambdas toward ~1.1 for close matches
    if rank_gap < 30:
        draw_target = 1.10
        draw_pull = 0.12 * (1 - rank_gap / 30)
        home_blend = home_blend * (1 - draw_pull) + draw_target * draw_pull
        away_blend = away_blend * (1 - draw_pull) + draw_target * draw_pull
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
    print("Patched! Changes:")
    print("  - Convergence range: < 30 -> < 40")
    print("  - Convergence strength: 25% -> 30%")
    print("  - Added draw boost toward lambda 1.1")
else:
    print("ERROR: Block not found!")
    # Debug
    if 'Close-match convergence' in code:
        lines = code.split('\n')
        for i, l in enumerate(lines):
            if 'Close-match' in l:
                for j in range(i, min(i+20, len(lines))):
                    print(f"  {j+1}: {lines[j].rstrip()}")
                break
    exit()

with open('content_automation.py', 'w', encoding='utf-8') as f:
    f.write(code)

import py_compile
try:
    py_compile.compile('content_automation.py', doraise=True)
    print("SYNTAX CHECK: OK")
except py_compile.PyCompileError as e:
    print(f"SYNTAX ERROR: {e}")
    with open('content_automation_backup.py', 'r', encoding='utf-8') as f:
        backup = f.read()
    with open('content_automation.py', 'w', encoding='utf-8') as f:
        f.write(backup)
    print("Backup restored!")
    exit()

import sys
for mod in list(sys.modules.keys()):
    if 'content' in mod or 'data_loader' in mod or 'strength' in mod or 'player' in mod:
        del sys.modules[mod]

from content_automation import quick_simulate

tests = [
    ('Argentina', 'Brazil', '~36/30/34'),
    ('Brazil', 'Argentina', '~34/30/36'),
    ('France', 'England', '~36/30/34'),
    ('Spain', 'Germany', '~35/30/35'),
    ('Bolivia', 'Suriname', '~45/28/27'),
    ('Brazil', 'India', '~65/20/15'),
    ('France', 'San Marino', '~90/7/3'),
    ('Norway', 'San Marino', '~85/10/5'),
    ('Colombia', 'Peru', '~38/30/32'),
    ('Germany', 'United States', '~40/28/32'),
]

print(f"\n  {'Matchup':<30s} {'Home':>6s} {'Draw':>6s} {'Away':>6s}  Target")
print("  " + "-" * 80)
for home, away, note in tests:
    r = quick_simulate(home, away)
    hw = r['home_win_pct']
    d = r['draw_pct']
    aw = r['away_win_pct']
    print(f"  {home+' v '+away:<30s} {hw:5.1f}% {d:5.1f}% {aw:5.1f}%  ({note})")
