
import argparse
import os
import sys
import webbrowser

from prediction_engine import predict, clean_match_type
from chart_generator import generate_all_charts


def print_divider():
    print("=" * 72)


def print_result(team_a, team_b, result):
    print_divider()
    print("MUNDIALISTA AI - MATCH PREDICTION")
    print_divider()
    print(f"{team_a} vs {team_b}")
    print(f"Match Type: {clean_match_type(result.get('match_type', 'Unknown'))}")
    print()

    fmt = "{:<20} Win: {:>6.1f}%"
    print(fmt.format(team_a, result.get("team_a_win", 0)))
    print("{:<20}    : {:>6.1f}%".format("Draw", result.get("draw", 0)))
    print(fmt.format(team_b, result.get("team_b_win", 0)))
    print()

    fmt2 = "{:<20} lambda: {:>6.2f}"
    print(fmt2.format(team_a, result.get("team_a_lambda", 0)))
    print(fmt2.format(team_b, result.get("team_b_lambda", 0)))
    print()

    print("{:<20} Rank: {}".format(team_a, result.get("team_a_rank", "N/A")))
    print("{:<20} Rank: {}".format(team_b, result.get("team_b_rank", "N/A")))
    print()

    top_scores = result.get("top_scores", [])
    if top_scores:
        print("Most Likely Scorelines:")
        for score in top_scores[:5]:
            if isinstance(score, (list, tuple)) and len(score) >= 2:
                print(f"  {str(score[0]):<8} {score[1]}")
            else:
                print(f"  {score}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Mundialista AI match prediction CLI")
    parser.add_argument("team_a", help="Home / Team A")
    parser.add_argument("team_b", help="Away / Team B")
    parser.add_argument("--home", help="Team with home advantage", default=None)
    parser.add_argument("--open", action="store_true", help="Open HTML report in browser")
    args = parser.parse_args()

    result = predict(args.team_a, args.team_b, home=args.home)
    print_result(args.team_a, args.team_b, result)

    print("Generating charts...")
    charts = generate_all_charts(result, args.team_a, args.team_b)
    print()
    print("Generated Files:")
    for k, v in charts.items():
        print(f"  {k:<12} {v}")

    if args.open and "html" in charts and os.path.exists(charts["html"]):
        webbrowser.open("file://" + os.path.abspath(charts["html"]))


if __name__ == "__main__":
    main()
