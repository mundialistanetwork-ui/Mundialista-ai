print("=" * 60)
print("  FIXING: RELATIVE STAR IMPACT + LAMBDA SPREAD CAP")
print("=" * 60)

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

with open('content_automation_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)

# Replace star impact + home advantage section
old_block = '''    # Apply star player impact
    home_star = get_team_star_impact(home_team)
    away_star = get_team_star_impact(away_team)
    home_blend *= home_star
    away_blend *= away_star
    # Apply home advantage (moderate - 4% boost)
    home_lambda = max(0.3, home_blend * 1.04)
    away_lambda = max(0.3, away_blend * 0.96)'''

new_block = '''    # Apply RELATIVE star player impact (cancels out when both have stars)
    home_star = get_team_star_impact(home_team)
    away_star = get_team_star_impact(away_team)
    avg_star = (home_star + away_star) / 2
    home_star_rel = home_star / avg_star if avg_star > 0 else 1.0
    away_star_rel = away_star / avg_star if avg_star > 0 else 1.0
    home_blend *= home_star_rel
    away_blend *= away_star_rel
    # Apply home advantage (moderate - 4% boost)
    home_blend *= 1.04
    away_blend *= 0.96
    # Cap lambda spread for top teams (prevent runaway predictions)
    if both_top:
        avg_lam = (home_blend + away_blend) / 2
        max_spread = 0.25  # max 25% difference from average
        home_blend = min(home_blend, avg_lam * (1 + max_spread))
        home_blend = max(home_blend, avg_lam * (1 - max_spread))
        away_blend = min(away_blend, avg_lam * (1 + max_spread))
        away_blend = max(away_blend, avg_lam * (1 - max_spread))
    home_lambda = max(0.3, home_blend)
    away_lambda = max(0.3, away_blend)'''

if old_block in code:
    code = code.replace(old_block, new_block)
    print("Patched! Changes:")
    print("  - Star impact now RELATIVE (1.2 vs 1.2 = no effect)")
    print("  - Lambda spread capped at 25% for top teams")
    print("  - Both stars at 1.2x now cancels out perfectly")
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
    ('France', 'San Marino', '~85/10/5'),
    ('Norway', 'San Marino', '~80/12/8'),
    ('Colombia', 'Peru', '~38/30/32'),
    ('Germany', 'United States', '~40/28/32'),
    ('Japan', 'South Korea', '~34/30/36'),
    ('Mexico', 'United States', '~35/30/35'),
]

print(f"\n  {'Matchup':<30s} {'Home':>6s} {'Draw':>6s} {'Away':>6s}  Target")
print("  " + "-" * 80)
for home, away, note in tests:
    r = quick_simulate(home, away)
    hw = r['home_win_pct']
    d = r['draw_pct']
    aw = r['away_win_pct']
    print(f"  {home+' v '+away:<30s} {hw:5.1f}% {d:5.1f}% {aw:5.1f}%  ({note})")
