from prediction_engine import load_results, load_goalscorers

df = load_results()
gs = load_goalscorers()

print("=== Results data ===")
print("Last date: " + str(df["date"].max()))
print("Total matches: " + str(len(df)))
print()
print("Last 5 matches in database:")
last5 = df.tail(5)[["date","home_team","away_team","home_score","away_score","tournament"]]
print(last5.to_string())
print()

swe = df[(df["home_team"]=="Sweden") | (df["away_team"]=="Sweden")].tail(3)
print("Last 3 Sweden matches:")
print(swe[["date","home_team","away_team","home_score","away_score","tournament"]].to_string())
print()

print("=== Goalscorers data ===")
print("Last date: " + str(gs["date"].max()))
print("Total goals: " + str(len(gs)))

gyo = gs[gs["scorer"].str.contains("keres", case=False, na=False)]
print()
print("Gyokeres goals in data: " + str(len(gyo)))
if not gyo.empty:
    print(gyo.tail(5).to_string())
