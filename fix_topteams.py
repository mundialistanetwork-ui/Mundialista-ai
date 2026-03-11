print("Aggressive rebalance for top team matchups...")

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

with open('content_automation_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)

# Replace the entire ranking blend section
old_block = '''    # Dynamic blend: 35% ranking baseline, up to 60% for huge gaps
    rank_gap = abs(h_rank - a_rank)
    rank_weight = min(0.60, 0.35 + rank_gap * 0.003)
    form_weight = 1.0 - rank_weight
    # Regress form toward global mean for stability
    home_lambda_form = 0.7 * home_lambda_raw + 0.3 * GLOBAL_GF
    away_lambda_form = 0.7 * away_lambda_raw + 0.3 * GLOBAL_GF
    # Blend form + ranking
    home_blend = form_weight * home_lambda_form + rank_weight * rank_home_lambda
    away_blend = form_weight * away_lambda_form + rank_weight * rank_away_lambda
    # Close-match convergence: push close teams toward equal
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
        away_blend = away_blend * (1 - draw_pull) + draw_target * draw_pull'''

new_block = '''    # Dynamic blend based on rank gap AND team tier
    rank_gap = abs(h_rank - a_rank)
    both_top = h_rank <= 25 and a_rank <= 25
    # Top teams: 50% ranking, others: 35% base
    if both_top:
        rank_weight = min(0.60, 0.50 + rank_gap * 0.002)
    else:
        rank_weight = min(0.65, 0.35 + rank_gap * 0.004)
    form_weight = 1.0 - rank_weight
    # Regress form HARD toward global mean (especially top teams)
    regress = 0.45 if both_top else 0.30
    home_lambda_form = (1 - regress) * home_lambda_raw + regress * GLOBAL_GF
    away_lambda_form = (1 - regress) * away_lambda_raw + regress * GLOBAL_GF
    # Blend form + ranking
    home_blend = form_weight * home_lambda_form + rank_weight * rank_home_lambda
    away_blend = form_weight * away_lambda_form + rank_weight * rank_away_lambda
    # Close-match convergence: push close teams toward equal
    if rank_gap < 40:
        converge_strength = 0.35 if both_top else 0.25
        avg_lambda = (home_blend + away_blend) / 2
        converge = converge_strength * (1 - rank_gap / 40)
        home_blend = home_blend * (1 - converge) + avg_lambda * converge
        away_blend = away_blend * (1 - converge) + avg_lambda * converge
    # Draw boost: push lambdas toward ~1.1 for close matches
    if rank_gap < 30:
        draw_target = 1.10
        draw_pull = 0.15 if both_top else 0.10
        draw_pull *= (1 - rank_gap / 30)
        home_blend = home_blend * (1 - draw_pull) + draw_target * draw_pull
        away_blend = away_blend * (1 - draw_pull) + draw_target * draw_pull'''

if old_block in code:
    code = code.replace(old_block, new_block)
    print("Replaced! Key changes:")
    print("  - Top 25 teams: 50% ranking weight (was 35%)")
    print("  - Top teams: 45% form regression (was 30%)")
    print("  - Top teams: 35% convergence (was 25%)")
    print("  - Top teams: 15% draw pull (was 12%)")
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
