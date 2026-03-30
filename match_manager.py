import pandas as pd
import os
import sys
from datetime import datetime

RECENT_RESULTS = "data/recent_results.csv"
RECENT_GOALS = "data/recent_goalscorers.csv"


def ensure_files():
    if not os.path.exists(RECENT_RESULTS):
        df = pd.DataFrame(columns=["date", "home_team", "away_team", "home_score", "away_score", "tournament", "city", "country", "neutral"])
        df.to_csv(RECENT_RESULTS, index=False)
        print("Created " + RECENT_RESULTS)
    if not os.path.exists(RECENT_GOALS):
        df = pd.DataFrame(columns=["date", "home_team", "away_team", "team", "scorer", "minute", "own_goal", "penalty"])
        df.to_csv(RECENT_GOALS, index=False)
        print("Created " + RECENT_GOALS)


def show_recent():
    ensure_files()
    results = pd.read_csv(RECENT_RESULTS)
    goals = pd.read_csv(RECENT_GOALS)
    print()
    print("=" * 60)
    print("  RECENT RESULTS (" + str(len(results)) + " matches)")
    print("=" * 60)
    if results.empty:
        print("  No recent results added yet.")
    else:
        for _, r in results.iterrows():
            print("  " + str(r["date"]) + "  " + str(r["home_team"]) + " " + str(r["home_score"]) + "-" + str(r["away_score"]) + " " + str(r["away_team"]) + "  [" + str(r["tournament"]) + "]")
    print()
    print("=" * 60)
    print("  RECENT GOALS (" + str(len(goals)) + " goals)")
    print("=" * 60)
    if goals.empty:
        print("  No recent goals added yet.")
    else:
        for _, g in goals.iterrows():
            pen = " (PEN)" if g.get("penalty", False) else ""
            og = " (OG)" if g.get("own_goal", False) else ""
            print("  " + str(g["date"]) + "  " + str(g["scorer"]) + " " + str(int(g["minute"])) + "'" + pen + og + "  [" + str(g["team"]) + "]")
    print()


def add_result():
    ensure_files()
    print()
    print("=== ADD MATCH RESULT ===")
    print()
    date = input("Date (YYYY-MM-DD): ").strip()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
        print("  Using today: " + date)
    home = input("Home team: ").strip()
    away = input("Away team: ").strip()
    score_h = input("Home score: ").strip()
    score_a = input("Away score: ").strip()
    print()
    print("Tournament options:")
    print("  1. FIFA World Cup qualification")
    print("  2. FIFA World Cup")
    print("  3. Friendly")
    print("  4. UEFA Euro")
    print("  5. Copa America")
    print("  6. UEFA Nations League")
    print("  7. Africa Cup of Nations")
    print("  8. AFC Asian Cup")
    print("  9. CONCACAF Gold Cup")
    print("  0. Other (type manually)")
    t_map = {
        "1": "FIFA World Cup qualification",
        "2": "FIFA World Cup",
        "3": "Friendly",
        "4": "UEFA Euro",
        "5": "Copa America",
        "6": "UEFA Nations League",
        "7": "Africa Cup of Nations",
        "8": "AFC Asian Cup",
        "9": "CONCACAF Gold Cup",
    }
    t_choice = input("Tournament [1-9 or 0]: ").strip()
    if t_choice in t_map:
        tournament = t_map[t_choice]
    else:
        tournament = input("Tournament name: ").strip()
    city = input("City (optional): ").strip() or ""
    country = input("Country (optional): ").strip() or ""
    neutral_str = input("Neutral venue? (y/n) [n]: ").strip().lower()
    neutral = neutral_str == "y"

    row = {
        "date": date,
        "home_team": home,
        "away_team": away,
        "home_score": int(score_h),
        "away_score": int(score_a),
        "tournament": tournament,
        "city": city,
        "country": country,
        "neutral": neutral,
    }

    df = pd.read_csv(RECENT_RESULTS)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(RECENT_RESULTS, index=False)
    print()
    print("  Added: " + home + " " + str(score_h) + "-" + str(score_a) + " " + away)
    print()

    add_goals = input("Add goalscorers? (y/n) [y]: ").strip().lower()
    if add_goals != "n":
        add_match_goals(date, home, away)

    clear_engine_cache()


def add_match_goals(date, home, away):
    ensure_files()
    print()
    print("=== ADD GOALS for " + home + " vs " + away + " ===")
    print("  Type: PlayerName MinuteNumber Team")
    print("  Add (P) for penalty, (OG) for own goal")
    print("  Type 'done' when finished")
    print()

    goals = []
    while True:
        line = input("  Goal: ").strip()
        if line.lower() == "done" or line == "":
            break

        is_pen = "(P)" in line.upper() or "(PEN)" in line.upper()
        is_og = "(OG)" in line.upper()
        line_clean = line.replace("(P)", "").replace("(p)", "").replace("(PEN)", "").replace("(pen)", "")
        line_clean = line_clean.replace("(OG)", "").replace("(og)", "").strip()

        parts = line_clean.rsplit(" ", 2)
        if len(parts) < 3:
            print("    Format: PlayerName Minute Team  (e.g., Gyokeres 15 Sweden)")
            continue

        team = parts[-1].strip()
        try:
            minute = int(parts[-2].strip().replace("'", ""))
        except ValueError:
            print("    Could not parse minute. Try again.")
            continue
        scorer = " ".join(parts[:-2]).strip()

        goal = {
            "date": date,
            "home_team": home,
            "away_team": away,
            "team": team,
            "scorer": scorer,
            "minute": minute,
            "own_goal": is_og,
            "penalty": is_pen,
        }
        goals.append(goal)
        pen_str = " (PEN)" if is_pen else ""
        og_str = " (OG)" if is_og else ""
        print("    Added: " + scorer + " " + str(minute) + "'" + pen_str + og_str + " [" + team + "]")

    if goals:
        df = pd.read_csv(RECENT_GOALS)
        df = pd.concat([df, pd.DataFrame(goals)], ignore_index=True)
        df.to_csv(RECENT_GOALS, index=False)
        print()
        print("  Saved " + str(len(goals)) + " goals")


def add_goals_standalone():
    ensure_files()
    print()
    date = input("Match date (YYYY-MM-DD): ").strip()
    home = input("Home team: ").strip()
    away = input("Away team: ").strip()
    add_match_goals(date, home, away)
    clear_engine_cache()


def delete_result():
    ensure_files()
    df = pd.read_csv(RECENT_RESULTS)
    if df.empty:
        print("  No results to delete.")
        return
    print()
    for i, r in df.iterrows():
        print("  [" + str(i) + "] " + str(r["date"]) + " " + str(r["home_team"]) + " " + str(r["home_score"]) + "-" + str(r["away_score"]) + " " + str(r["away_team"]))
    print()
    idx = input("Delete which index? ").strip()
    try:
        idx = int(idx)
        row = df.iloc[idx]
        match_date = str(row["date"])
        match_home = str(row["home_team"])
        match_away = str(row["away_team"])
        df = df.drop(idx).reset_index(drop=True)
        df.to_csv(RECENT_RESULTS, index=False)
        print("  Deleted result.")

        gdf = pd.read_csv(RECENT_GOALS)
        gdf["date"] = gdf["date"].astype(str)
        before = len(gdf)
        gdf = gdf[~((gdf["date"] == match_date) & (gdf["home_team"] == match_home) & (gdf["away_team"] == match_away))]
        after = len(gdf)
        gdf.to_csv(RECENT_GOALS, index=False)
        print("  Removed " + str(before - after) + " associated goals.")
    except (ValueError, IndexError):
        print("  Invalid index.")
    clear_engine_cache()


def quick_predict():
    try:
        from prediction_engine import predict, clear_cache
        clear_cache()
    except ImportError:
        from prediction_engine import predict

    print()
    team_a = input("Team A: ").strip()
    team_b = input("Team B: ").strip()
    r = predict(team_a, team_b)
    print()
    print("  " + team_a + " vs " + team_b + "  [" + r.get("match_type", "?") + "]")
    print("  " + str(r["team_a_win"]) + "% | " + str(r["draw"]) + "% | " + str(r["team_b_win"]) + "%")
    print("  xG: " + str(r["team_a_lambda"]) + " - " + str(r["team_b_lambda"]))
    print("  Stars A: " + str(r["team_a_stars"][:3]) + " boost=" + str(r["team_a_star_boost"]))
    print("  Stars B: " + str(r["team_b_stars"][:3]) + " boost=" + str(r["team_b_star_boost"]))
    h2h = r.get("h2h_matches", 0)
    print("  H2H: " + str(h2h) + " matches (" + str(r.get("h2h_wins_a", 0)) + "W-" + str(r.get("h2h_draws", 0)) + "D-" + str(r.get("h2h_wins_b", 0)) + "L)")
    print("  Top: ", end="")
    for s in r["top_scores"][:5]:
        print(str(s[0]) + " ", end="")
    print()


def estimate_cards(team_a, team_b):
    try:
        from prediction_engine import get_team_stats, get_team_ranking
    except ImportError:
        print("  Engine not available")
        return

    stats_a = get_team_stats(team_a)
    stats_b = get_team_stats(team_b)
    rank_a = get_team_ranking(team_a)
    rank_b = get_team_ranking(team_b)

    base_yellow = 2.8
    base_red = 0.08

    rank_gap = abs(rank_a - rank_b)
    if rank_gap > 50:
        intensity = 0.85
    elif rank_gap < 15:
        intensity = 1.25
    else:
        intensity = 1.0

    aggression_a = stats_a.get("defense", 1.0) * 0.6 + stats_a.get("avg_ga", 1.36) * 0.2
    aggression_b = stats_b.get("defense", 1.0) * 0.6 + stats_b.get("avg_ga", 1.36) * 0.2

    yellows_a = base_yellow * 0.5 * intensity * aggression_a
    yellows_b = base_yellow * 0.5 * intensity * aggression_b
    total_yellows = yellows_a + yellows_b

    red_factor = intensity * 1.0
    if total_yellows > 4.0:
        red_factor *= 1.3
    total_reds = base_red * red_factor * 2

    import random
    random.seed(hash(team_a + team_b + str(rank_a)))
    red_prob = min(total_reds * 4, 0.35)

    print()
    print("  === CARD PREDICTION ===")
    print("  " + team_a + ": ~" + str(round(yellows_a, 1)) + " yellows")
    print("  " + team_b + ": ~" + str(round(yellows_b, 1)) + " yellows")
    print("  Total yellows: ~" + str(round(total_yellows, 1)))
    print("  Red card probability: " + str(round(100 * red_prob, 1)) + "%")
    print()

    if red_prob > 0.25:
        print("  \U0001f7e5 HIGH red card risk! Heated match expected.")
    elif red_prob > 0.15:
        print("  \U0001f7e8 Moderate red card risk.")
    else:
        print("  \U0001f7e9 Low red card risk.")

    if total_yellows > 5:
        print("  \U0001f4a2 Expect a physical, card-heavy match!")
    elif total_yellows > 3.5:
        print("  \u26a0\ufe0f A few cards likely. Competitive intensity.")
    else:
        print("  \u2705 Clean match expected.")


def card_predict_cli():
    print()
    team_a = input("Team A: ").strip()
    team_b = input("Team B: ").strip()
    estimate_cards(team_a, team_b)


def clear_engine_cache():
    try:
        from prediction_engine import clear_cache
        clear_cache()
        print("  Engine cache cleared.")
    except (ImportError, Exception):
        pass


def main():
    print()
    print("=" * 50)
    print("  MUNDIALISTA AI - MATCH MANAGER")
    print("  v6.1 CLI Tool")
    print("=" * 50)

    while True:
        print()
        print("  1. Show recent results & goals")
        print("  2. Add match result + goals")
        print("  3. Add goals to existing match")
        print("  4. Delete a result")
        print("  5. Quick predict")
        print("  6. Card prediction")
        print("  7. Exit")
        print()
        choice = input("  Choice [1-7]: ").strip()

        if choice == "1":
            show_recent()
        elif choice == "2":
            add_result()
        elif choice == "3":
            add_goals_standalone()
        elif choice == "4":
            delete_result()
        elif choice == "5":
            quick_predict()
        elif choice == "6":
            card_predict_cli()
        elif choice == "7":
            print("  Bye!")
            break
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()
