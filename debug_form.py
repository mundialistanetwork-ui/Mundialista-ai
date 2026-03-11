import sys
for mod in list(sys.modules.keys()):
    if 'content' in mod or 'data_loader' in mod or 'strength' in mod:
        del sys.modules[mod]

from content_automation import quick_simulate, get_team_stats, RESULTS_DF, GLOBAL_GF, GLOBAL_GA, TEAM_RATINGS
from strength_adjust import get_adjusted_stats

print("GLOBAL_GF:", GLOBAL_GF)
print("GLOBAL_GA:", GLOBAL_GA)
print()

pairs = [
    ('Argentina', 'Brazil'),
    ('Spain', 'Germany'),
    ('France', 'San Marino'),
]

for home, away in pairs:
    print(f"=== {home} vs {away} ===")
    hs = get_team_stats(RESULTS_DF, home)
    as_ = get_team_stats(RESULTS_DF, away)
    print(f"  {home} raw: gf={hs['avg_gf']:.2f} ga={hs['avg_ga']:.2f} n={hs['n_matches']}")
    print(f"  {away} raw: gf={as_['avg_gf']:.2f} ga={as_['avg_ga']:.2f} n={as_['n_matches']}")
    
    h_adj = get_adjusted_stats(RESULTS_DF, home, TEAM_RATINGS)
    a_adj = get_adjusted_stats(RESULTS_DF, away, TEAM_RATINGS)
    if h_adj:
        print(f"  {home} adjusted: gf={h_adj['blended_gf']:.2f} ga={h_adj['blended_ga']:.2f}")
    if a_adj:
        print(f"  {away} adjusted: gf={a_adj['blended_gf']:.2f} ga={a_adj['blended_ga']:.2f}")
    print()
