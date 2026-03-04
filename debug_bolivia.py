from data_loader import load_results, get_team_stats_for_app
import numpy as np

results = load_results()

for team in ['Bolivia', 'Suriname']:
    opponent = 'Bolivia' if team == 'Suriname' else 'Suriname'
    stats = get_team_stats_for_app(results, team, opponent)
    if stats:
        print(f"{team}:")
        print(f"  Matches: {stats['n_matches']}")
        print(f"  Avg Goals For: {float(stats['avg_gf']):.2f}")
        print(f"  Avg Goals Against: {float(stats['avg_ga']):.2f}")
        print(f"  Goal Diff: {float(stats['avg_gf']) - float(stats['avg_ga']):+.2f}")
        print()

print("BOLIVIA recent matches:")
bol_h = results[results['home_team'] == 'Bolivia'].tail(10)
bol_a = results[results['away_team'] == 'Bolivia'].tail(10)
for _, r in bol_h.iterrows():
    print(f"  Bolivia {int(r['home_score'])}-{int(r['away_score'])} {r['away_team']}")
for _, r in bol_a.iterrows():
    print(f"  {r['home_team']} {int(r['home_score'])}-{int(r['away_score'])} Bolivia")

print()
print("SURINAME recent matches:")
sur_h = results[results['home_team'] == 'Suriname'].tail(10)
sur_a = results[results['away_team'] == 'Suriname'].tail(10)
for _, r in sur_h.iterrows():
    print(f"  Suriname {int(r['home_score'])}-{int(r['away_score'])} {r['away_team']}")
for _, r in sur_a.iterrows():
    print(f"  {r['home_team']} {int(r['home_score'])}-{int(r['away_score'])} Suriname")