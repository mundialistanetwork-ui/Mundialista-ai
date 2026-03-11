print("=" * 60)
print("  FIXING GLOBAL BASELINE + LAST 12 MATCHES + SHRINKAGE")
print("=" * 60)

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

with open('content_automation_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)

# Fix 1: Change last_n from 7 to 12
old_def = 'def get_team_stats(results, team, last_n=7):'
new_def = 'def get_team_stats(results, team, last_n=12):'

if old_def in code:
    code = code.replace(old_def, new_def)
    print("Changed last_n from 7 to 12")
else:
    print("WARN: Could not find last_n=7, checking current value...")
    import re
    match = re.search(r'def get_team_stats\(results, team, last_n=(\d+)\)', code)
    if match:
        old_val = match.group(1)
        print(f"  Found last_n={old_val}, replacing...")
        code = code.replace(f'last_n={old_val})', 'last_n=12)')
        print("  Changed to last_n=12")

# Fix 2: Replace broken median-based globals with actual match averages
old_global = '''GLOBAL_GF = float(np.median(_all_gf)) if _all_gf else 1.2
GLOBAL_GA = float(np.median(_all_ga)) if _all_ga else 1.2
print(f"Global baseline: {GLOBAL_GF:.2f} GF / {GLOBAL_GA:.2f} GA")'''

new_global = '''# Use actual match averages (GF must equal GA globally)
_true_gf = float(RESULTS_DF["home_score"].mean() + RESULTS_DF["away_score"].mean()) / 2
GLOBAL_GF = _true_gf
GLOBAL_GA = _true_gf  # By definition, global GF == global GA
print(f"Global baseline: {GLOBAL_GF:.2f} GF / {GLOBAL_GA:.2f} GA (symmetric)")'''

if old_global in code:
    code = code.replace(old_global, new_global)
    print("Fixed global baseline to use actual match averages")
else:
    print("ERROR: Could not find global baseline code!")
    exit()

# Fix 3: Increase shrinkage for 12-match form
old_shrink = '    shrink_k = 8'
new_shrink = '    shrink_k = 10  # Balanced shrinkage for 12-match form window'

if old_shrink in code:
    code = code.replace(old_shrink, new_shrink)
    print("Increased shrinkage from 8 to 10")
else:
    print("WARN: Could not find shrink_k=8")

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
