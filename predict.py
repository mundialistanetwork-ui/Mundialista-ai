from content_automation import quick_simulate
import sys

if len(sys.argv) >= 3:
    home = sys.argv[1]
    away = sys.argv[2]
else:
    home = input("Home team: ")
    away = input("Away team: ")

r = quick_simulate(home, away)
print()
print(f"  {home} vs {away}")
print(f"  {'='*40}")
print(f"  {home:>20s}: {r['home_win_pct']:.1f}%")
print(f"  {'Draw':>20s}: {r['draw_pct']:.1f}%")
print(f"  {away:>20s}: {r['away_win_pct']:.1f}%")
print(f"  {'='*40}")
print(f"  Favourite: {r['favourite']}")
print(f"  Expected goals: {r['home_exp']:.1f} - {r['away_exp']:.1f}")
print()
