import sys, pandas as pd, numpy as np
sys.path.insert(0, ".")
from data_loader import load_results, get_all_teams, get_team_stats_for_app, get_team_matches
from scipy.stats import poisson

r = load_results(years_lookback=4)

def header(n, title):
    print(f"\n{'='*60}")
    print(f"  PREDICTION CHEAT CODE #{n}: {title}")
    print(f"{'='*60}")

# ── 1. MODEL ACCURACY BACKTEST ─────────────────────────────────
header(1, "Backtest: did the model pick the right winner?")
# Use last 100 matches as test set, train on everything before
r["date"] = pd.to_datetime(r["date"])
r_sorted = r.sort_values("date")
train = r_sorted.iloc[:-100]
test  = r_sorted.iloc[-100:]

correct = 0
total = 0
for _, row in test.iterrows():
    ht = row["home_team"]
    at = row["away_team"]
    hs = get_team_stats_for_app(train, ht, at)
    as_ = get_team_stats_for_app(train, at, ht)
    if hs is None or as_ is None:
        continue
    # Simple Poisson prediction (no full MCMC — just lambda)
    pred_home = hs["avg_gf"] * (as_["avg_ga"] / 1.3)
    pred_away = as_["avg_gf"] * (hs["avg_ga"] / 1.3)
    if pred_home > pred_away:
        pred = "home"
    elif pred_away > pred_home:
        pred = "away"
    else:
        pred = "draw"
    if row["home_score"] > row["away_score"]:
        actual = "home"
    elif row["away_score"] > row["home_score"]:
        actual = "away"
    else:
        actual = "draw"
    if pred == actual:
        correct += 1
    total += 1

print(f"  Correct predictions: {correct}/{total} ({correct/total*100:.1f}%)")
print(f"  Random baseline:     33.3%")
print(f"  Improvement over random: +{correct/total*100 - 33.3:.1f}%")

# ── 2. WHERE DOES THE MODEL FAIL MOST? ────────────────────────
header(2, "Where model fails — by tournament type")
failures = {"Friendly": [0,0], "Qualification": [0,0], "Competition": [0,0]}
for _, row in test.iterrows():
    ht = row["home_team"]
    at = row["away_team"]
    hs = get_team_stats_for_app(train, ht, at)
    as_ = get_team_stats_for_app(train, at, ht)
    if hs is None or as_ is None:
        continue
    pred_home = hs["avg_gf"] * (as_["avg_ga"] / 1.3)
    pred_away = as_["avg_gf"] * (hs["avg_ga"] / 1.3)
    pred = "home" if pred_home > pred_away else "away" if pred_away > pred_home else "draw"
    actual = "home" if row["home_score"] > row["away_score"] else "away" if row["away_score"] > row["home_score"] else "draw"
    tourn = str(row["tournament"]).lower()
    if "friendly" in tourn:
        key = "Friendly"
    elif any(x in tourn for x in ["qualif", "qualifier", "wcq", "acq"]):
        key = "Qualification"
    else:
        key = "Competition"
    failures[key][1] += 1
    if pred == actual:
        failures[key][0] += 1
for k, (correct, total) in failures.items():
    if total > 0:
        print(f"  {k:<20} {correct}/{total} correct ({correct/total*100:.1f}%)")

# ── 3. UPSET DETECTION RATE ───────────────────────────────────
header(3, "How often does the model detect real upsets?")
upset_detected = 0
upset_missed = 0
false_upsets = 0
for _, row in test.iterrows():
    ht = row["home_team"]
    at = row["away_team"]
    hs = get_team_stats_for_app(train, ht, at)
    as_ = get_team_stats_for_app(train, at, ht)
    if hs is None or as_ is None:
        continue
    pred_fav = "home" if hs["avg_gf"] >= as_["avg_gf"] else "away"
    actual_winner = "home" if row["home_score"] > row["away_score"] else "away" if row["away_score"] > row["home_score"] else "draw"
    real_upset = (actual_winner != pred_fav and actual_winner != "draw")
    if real_upset:
        if actual_winner != pred_fav:
            upset_missed += 1
        else:
            upset_detected += 1
total_upsets = upset_detected + upset_missed
print(f"  Real upsets in test set:    {total_upsets}")
print(f"  Upsets detected by model:   {upset_detected}")
print(f"  Upsets missed:              {upset_missed}")
if total_upsets > 0:
    print(f"  Upset detection rate:       {upset_detected/total_upsets*100:.1f}%")

# ── 4. GOAL PREDICTION ACCURACY ───────────────────────────────
header(4, "How close are predicted goals to real goals?")
errors_home = []
errors_away = []
for _, row in test.iterrows():
    hs = get_team_stats_for_app(train, row["home_team"], row["away_team"])
    as_ = get_team_stats_for_app(train, row["away_team"], row["home_team"])
    if hs is None or as_ is None:
        continue
    pred_h = hs["avg_gf"] * (as_["avg_ga"] / 1.3)
    pred_a = as_["avg_gf"] * (hs["avg_ga"] / 1.3)
    errors_home.append(abs(pred_h - row["home_score"]))
    errors_away.append(abs(pred_a - row["away_score"]))
print(f"  Avg home goal error (MAE):  {np.mean(errors_home):.2f} goals")
print(f"  Avg away goal error (MAE):  {np.mean(errors_away):.2f} goals")
print(f"  Combined MAE:               {np.mean(errors_home + errors_away):.2f} goals")
print(f"  (A good model scores < 1.0)")

# ── 5. SCORELINE PROBABILITY CALIBRATION ──────────────────────
header(5, "Most predicted scoreline vs most common real scoreline")
pred_scores = []
real_scores = []
for _, row in test.iterrows():
    hs = get_team_stats_for_app(train, row["home_team"], row["away_team"])
    as_ = get_team_stats_for_app(train, row["away_team"], row["home_team"])
    if hs is None or as_ is None:
        continue
    ph = hs["avg_gf"] * (as_["avg_ga"] / 1.3)
    pa = as_["avg_gf"] * (hs["avg_ga"] / 1.3)
    pred_h = int(round(ph))
    pred_a = int(round(pa))
    pred_scores.append(f"{pred_h}-{pred_a}")
    real_scores.append(f"{int(row['home_score'])}-{int(row['away_score'])}")
from collections import Counter
print(f"  Top 5 PREDICTED scorelines:")
for s, c in Counter(pred_scores).most_common(5):
    print(f"    {s:<8} predicted {c} times")
print(f"  Top 5 REAL scorelines:")
for s, c in Counter(real_scores).most_common(5):
    print(f"    {s:<8} happened {c} times")

# ── 6. CONFIDENCE VS ACCURACY ─────────────────────────────────
header(6, "Does high model confidence = more accurate?")
buckets = {"High (>65%)": [0,0], "Medium (45-65%)": [0,0], "Low (<45%)": [0,0]}
for _, row in test.iterrows():
    hs = get_team_stats_for_app(train, row["home_team"], row["away_team"])
    as_ = get_team_stats_for_app(train, row["away_team"], row["home_team"])
    if hs is None or as_ is None:
        continue
    ph = hs["avg_gf"] * (as_["avg_ga"] / 1.3)
    pa = as_["avg_gf"] * (hs["avg_ga"] / 1.3)
    total_rate = ph + pa
    home_conf = ph / total_rate * 100 if total_rate > 0 else 50
    pred = "home" if ph > pa else "away"
    actual = "home" if row["home_score"] > row["away_score"] else "away" if row["away_score"] > row["home_score"] else "draw"
    conf = max(home_conf, 100 - home_conf)
    if conf > 65:
        key = "High (>65%)"
    elif conf > 45:
        key = "Medium (45-65%)"
    else:
        key = "Low (<45%)"
    buckets[key][1] += 1
    if pred == actual:
        buckets[key][0] += 1
for k, (c, t) in buckets.items():
    if t > 0:
        print(f"  {k:<20} {c}/{t} correct ({c/t*100:.1f}%)")

# ── 7. HOME ADVANTAGE IN YOUR PREDICTIONS ─────────────────────
header(7, "Is home advantage baked into predictions correctly?")
home_pred_wins = 0
home_real_wins = 0
total = 0
for _, row in test.iterrows():
    hs = get_team_stats_for_app(train, row["home_team"], row["away_team"])
    as_ = get_team_stats_for_app(train, row["away_team"], row["home_team"])
    if hs is None or as_ is None:
        continue
    ph = hs["avg_gf"] * (as_["avg_ga"] / 1.3)
    pa = as_["avg_gf"] * (hs["avg_ga"] / 1.3)
    if ph > pa:
        home_pred_wins += 1
    if row["home_score"] > row["away_score"]:
        home_real_wins += 1
    total += 1
print(f"  Model predicts home win:  {home_pred_wins}/{total} ({home_pred_wins/total*100:.1f}%)")
print(f"  Real home win rate:       {home_real_wins}/{total} ({home_real_wins/total*100:.1f}%)")
diff = home_pred_wins/total*100 - home_real_wins/total*100
print(f"  Gap: {diff:+.1f}% ({'model overestimates home' if diff > 0 else 'model underestimates home'})")

# ── 8. DRAW PREDICTION ACCURACY ───────────────────────────────
header(8, "Draw prediction — hardest thing in football")
draw_pred = 0
draw_real = 0
draw_correct = 0
for _, row in test.iterrows():
    hs = get_team_stats_for_app(train, row["home_team"], row["away_team"])
    as_ = get_team_stats_for_app(train, row["away_team"], row["home_team"])
    if hs is None or as_ is None:
        continue
    ph = hs["avg_gf"] * (as_["avg_ga"] / 1.3)
    pa = as_["avg_gf"] * (hs["avg_ga"] / 1.3)
    pred_draw = abs(ph - pa) < 0.15
    real_draw = row["home_score"] == row["away_score"]
    if pred_draw:
        draw_pred += 1
    if real_draw:
        draw_real += 1
    if pred_draw and real_draw:
        draw_correct += 1
print(f"  Model predicted draws:    {draw_pred}")
print(f"  Real draws in test set:   {draw_real}")
print(f"  Correctly called draws:   {draw_correct}")
print(f"  Draw accuracy:            {draw_correct/max(draw_real,1)*100:.1f}%")
print(f"  (Anything above 30% is good — draws are near-random)")

# ── 9. BEST PREDICTED MATCHUPS (most data) ────────────────────
header(9, "Most reliable predicted matchups (most combined data)")
rows_out = []
teams = get_all_teams(r)
checked = set()
for t1 in teams[:30]:
    for t2 in teams[:30]:
        if t1 == t2 or (t2,t1) in checked:
            continue
        checked.add((t1,t2))
        s1 = get_team_stats_for_app(r, t1, t2)
        s2 = get_team_stats_for_app(r, t2, t1)
        if s1 and s2:
            combined = s1["n_matches"] + s2["n_matches"]
            rows_out.append((t1, t2, combined, s1["h2h_n"]))
rows_out.sort(key=lambda x: -x[2])
print(f"  {'Home':<22} {'Away':<22} {'Combined n':>10} {'H2H':>6}")
print(f"  {'-'*62}")
for t1, t2, cn, h2h in rows_out[:10]:
    print(f"  {t1:<22} {t2:<22} {cn:>10} {h2h:>6}")

# ── 10. WORST PREDICTED MATCHUPS (least data) ─────────────────
header(10, "Least reliable matchups — treat with suspicion!")
rows_out.sort(key=lambda x: x[2])
print(f"  {'Home':<22} {'Away':<22} {'Combined n':>10} {'H2H':>6}")
print(f"  {'-'*62}")
for t1, t2, cn, h2h in rows_out[:10]:
    print(f"  ⚠️  {t1:<20} {t2:<20} {cn:>10} {h2h:>6}")

# ── 11. GOALS DISTRIBUTION — MODEL VS REALITY ─────────────────
header(11, "Goals distribution: what Poisson thinks vs what happened")
real_goals = pd.concat([r["home_score"], r["away_score"]]).astype(int)
avg_lambda = real_goals.mean()
print(f"  Avg goals per team per game (real): {avg_lambda:.3f}")
print(f"\n  Goals  Real%   Poisson%  Difference")
print(f"  {'─'*40}")
for g in range(7):
    real_pct = (real_goals == g).mean() * 100
    poisson_pct = poisson.pmf(g, avg_lambda) * 100
    diff = real_pct - poisson_pct
    flag = " ← model underestimates" if diff > 2 else " ← model overestimates" if diff < -2 else ""
    print(f"  {g}      {real_pct:>5.1f}%   {poisson_pct:>5.1f}%   {diff:>+5.1f}%{flag}")

# ── 12. COMPETITIVE VS FRIENDLY PREDICTION GAP ────────────────
header(12, "Competitive vs friendly: which is easier to predict?")
for label, mask in [("Friendly", r["tournament"].str.contains("Friendly", case=False, na=False)),
                     ("Competitive", ~r["tournament"].str.contains("Friendly", case=False, na=False))]:
    grp = r[mask].tail(50)
    correct = 0
    total = 0
    for _, row in grp.iterrows():
        hs = get_team_stats_for_app(r, row["home_team"], row["away_team"])
        as_ = get_team_stats_for_app(r, row["away_team"], row["home_team"])
        if hs is None or as_ is None:
            continue
        ph = hs["avg_gf"] * (as_["avg_ga"] / 1.3)
        pa = as_["avg_gf"] * (hs["avg_ga"] / 1.3)
        pred = "home" if ph > pa else "away"
        actual = "home" if row["home_score"] > row["away_score"] else "away" if row["away_score"] > row["home_score"] else "draw"
        if pred == actual:
            correct += 1
        total += 1
    if total > 0:
        print(f"  {label:<15} {correct}/{total} correct ({correct/total*100:.1f}%)")

# ── 13. RECENT FORM WEIGHT CHECK ──────────────────────────────
header(13, "Does recent form (last 5) predict better than full history?")
for window, label in [(5, "Last 5 matches"), (40, "Last 40 matches")]:
    correct = 0
    total = 0
    for _, row in test.iterrows():
        team_matches_h = get_team_matches(train, row["home_team"]).head(window)
        team_matches_a = get_team_matches(train, row["away_team"]).head(window)
        if len(team_matches_h) < 3 or len(team_matches_a) < 3:
            continue
        ph = team_matches_h["goals_for"].mean()
        pa = team_matches_a["goals_for"].mean()
        pred = "home" if ph > pa else "away"
        actual = "home" if row["home_score"] > row["away_score"] else "away" if row["away_score"] > row["home_score"] else "draw"
        if pred == actual:
            correct += 1
        total += 1
    if total > 0:
        print(f"  {label:<20} {correct}/{total} correct ({correct/total*100:.1f}%)")

# ── 14. HIGH GOAL GAMES — MODEL BLINDSPOT? ────────────────────
header(14, "High scoring games (4+ goals) — does model predict them?")
high_score = test[test["home_score"] + test["away_score"] >= 4]
correct = 0
total = 0
for _, row in high_score.iterrows():
    hs = get_team_stats_for_app(train, row["home_team"], row["away_team"])
    as_ = get_team_stats_for_app(train, row["away_team"], row["home_team"])
    if hs is None or as_ is None:
        continue
    ph = hs["avg_gf"] * (as_["avg_ga"] / 1.3)
    pa = as_["avg_gf"] * (hs["avg_ga"] / 1.3)
    pred = "home" if ph > pa else "away"
    actual = "home" if row["home_score"] > row["away_score"] else "away" if row["away_score"] > row["home_score"] else "draw"
    if pred == actual:
        correct += 1
    total += 1
print(f"  High-scoring games in test: {len(high_score)}")
if total > 0:
    print(f"  Model accuracy on these:    {correct}/{total} ({correct/total*100:.1f}%)")
print(f"  (If much lower than overall accuracy → model misses open games)")

# ── 15. OVERALL MODEL REPORT CARD ─────────────────────────────
header(15, "OVERALL MODEL REPORT CARD")
print(f"""
  Metric                          Score
  ─────────────────────────────────────────────────────
  Overall winner prediction       Run #1 to see
  Goal prediction MAE             Run #4 to see
  Draw accuracy                   Run #8 to see (hardest)
  Home advantage calibration      Run #7 to see
  Competitive match accuracy      Run #12 to see
  Recent form vs full history     Run #13 to see

  Grade thresholds:
  ✅  >55% winner accuracy  = GOOD  (Vegas books hit ~60%)
  ⚠️  45-55%               = OKAY  (better than random)
  ❌  <45%                 = NEEDS WORK
  
  Key insight: if competitive >> friendly accuracy,
  consider filtering friendlies from training data entirely.
  If last-5 >> last-40, reduce last_n in data_loader.py.
""")

print(f"\n{'='*60}")
print(f"  ALL 15 PREDICTION CHEAT CODES COMPLETE")
print(f"{'='*60}\n")
