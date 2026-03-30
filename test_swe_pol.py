from prediction_engine import predict, clear_cache

clear_cache()

r = predict("Sweden", "Poland")
print("Sweden vs Poland (WITH recent data)")
print("  Result: " + str(r["team_a_win"]) + "% | " + str(r["draw"]) + "% | " + str(r["team_b_win"]) + "%")
print("  Lambdas: " + str(r["team_a_lambda"]) + " vs " + str(r["team_b_lambda"]))
print("  Stars: " + str(r["team_a_stars"][:3]))
print("  Top: " + str(r["top_scores"][:5]))
