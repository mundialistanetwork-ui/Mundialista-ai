from prediction_engine import predict, get_team_stats, get_team_ranking
import pandas as pd

# Check Sweden's recent results to understand the 1.213 defense
from prediction_engine import load_results
df = load_results()

swe_home = df[df["home_team"] == "Sweden"].tail(10)[["date","home_team","away_team","home_score","away_score","tournament"]]
swe_away = df[df["away_team"] == "Sweden"].tail(10)[["date","home_team","away_team","home_score","away_score","tournament"]]

print("=== Sweden LAST 10 HOME ===")
print(swe_home.to_string())
print()
print("=== Sweden LAST 10 AWAY ===")
print(swe_away.to_string())
print()

# Average goals conceded
home_ga = swe_home["away_score"].mean()
away_ga = swe_away["home_score"].mean()
print("Avg GA home: " + str(round(home_ga, 2)))
print("Avg GA away: " + str(round(away_ga, 2)))
print()

# Same for Poland
pol_home = df[df["home_team"] == "Poland"].tail(10)[["date","home_team","away_team","home_score","away_score","tournament"]]
pol_away = df[df["away_team"] == "Poland"].tail(10)[["date","home_team","away_team","home_score","away_score","tournament"]]
print("=== Poland LAST 10 HOME ===")
print(pol_home.to_string())
print()
print("=== Poland LAST 10 AWAY ===")
print(pol_away.to_string())
