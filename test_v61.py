from prediction_engine import predict

tests = [
    ("Argentina", "Brazil"),
    ("Spain", "Germany"),
    ("France", "San Marino"),
    ("Italy", "France"),
    ("Brazil", "Bolivia"),
]

for a, b in tests:
    r = predict(a, b)
    mt = r.get("match_type", "?")
    print(a + " vs " + b + "  [" + mt + "]")
    print("  Result: " + str(r["team_a_win"]) + "% | " + str(r["draw"]) + "% | " + str(r["team_b_win"]) + "%")
    print("  Lambdas: " + str(r["team_a_lambda"]) + " vs " + str(r["team_b_lambda"]))
    sa = r["team_a_stars"][:4]
    sb = r["team_b_stars"][:4]
    print("  Stars A: " + str(sa) + "  boost=" + str(r["team_a_star_boost"]))
    print("  Stars B: " + str(sb) + "  boost=" + str(r["team_b_star_boost"]))
    h2h = r.get("h2h_matches", 0)
    wa = r.get("h2h_wins_a", 0)
    wb = r.get("h2h_wins_b", 0)
    d = r.get("h2h_draws", 0)
    print("  H2H: " + str(h2h) + " matches (" + str(wa) + "W-" + str(d) + "D-" + str(wb) + "L)")
    scores = r["top_scores"][:6]
    print("  Top scores: " + str(scores))
    print()
