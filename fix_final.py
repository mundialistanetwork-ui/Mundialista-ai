print("Final tweak: tighter spread cap...")

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

with open('content_automation_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)

code = code.replace(
    '        max_spread = 0.25  # max 25% difference from average',
    '        max_spread = 0.18  # max 18% difference from average'
)
print("Changed spread cap from 25% to 18%")

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
    ('Argentina', 'Brazil', '~38/28/34'),
    ('Brazil', 'Argentina', '~34/28/38'),
    ('France', 'England', '~36/28/36'),
    ('Spain', 'Germany', '~36/28/36'),
    ('Bolivia', 'Suriname', '~45/28/27'),
    ('Brazil', 'India', '~65/20/15'),
    ('France', 'San Marino', '~85/10/5'),
    ('Norway', 'San Marino', '~80/12/8'),
    ('Colombia', 'Peru', '~40/28/32'),
    ('Germany', 'United States', '~40/28/32'),
    ('Mexico', 'United States', '~35/28/37'),
]

print(f"\n  {'Matchup':<30s} {'Home':>6s} {'Draw':>6s} {'Away':>6s}  Target")
print("  " + "-" * 80)
for home, away, note in tests:
    r = quick_simulate(home, away)
    hw = r['home_win_pct']
    d = r['draw_pct']
    aw = r['away_win_pct']
    print(f"  {home+' v '+away:<30s} {hw:5.1f}% {d:5.1f}% {aw:5.1f}%  ({note})")
