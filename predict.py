import argparse
import os
import sys
import webbrowser

from prediction_engine import predict
from chart_generator import generate_all_charts

def print_divider():
    print("=" * 72)

def print_result(team_a, team_b, result):
    print_divider()
    print("MUNDIALISTA AI - MATCH PREDICTION")
    print_divider()
    print(team_a + " vs " + team_b)
    print("Match Type: " + result.get("match_type", "Competitive"))
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
        for item in top_scores[:5]:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                print("  {:<8} {}".format(item[0], item[1]))
            else:
                print("  {}".format(item))
        print()

def interactive_mode():
    print_divider()
    print("MUNDIALISTA AI - INTERACTIVE MODE")
    print_divider()
    team_a = input("Enter Team A: ").strip()
    team_b = input("Enter Team B: ").strip()
    open_report = input("Open HTML report? (y/n): ").strip().lower() in ["y", "yes"]
    return team_a, team_b, open_report

def main():
    parser = argparse.ArgumentParser(description="Predict international football matches.")
    parser.add_argument("team_a", nargs="?", help="First team")
    parser.add_argument("team_b", nargs="?", help="Second team")
    parser.add_argument("--open", "-o", dest="open_report", action="store_true",
                        help="Open HTML report in browser after generation")

    args = parser.parse_args()

    if args.team_a and args.team_b:
        team_a = args.team_a
        team_b = args.team_b
        open_report = args.open_report
    else:
        team_a, team_b, open_report = interactive_mode()

    if not team_a or not team_b:
        print("Error: Two teams are required.")
        sys.exit(1)

    if team_a == team_b:
        print("Error: Please choose two different teams.")
        sys.exit(1)

    try:
        result = predict(team_a, team_b)
    except Exception as e:
        print("Prediction failed: " + str(e))
        sys.exit(1)

    print_result(team_a, team_b, result)

    print("Generating charts...")
    try:
        charts = generate_all_charts(result, team_a, team_b)
        print()
        print("Generated Files:")
        for key, path in charts.items():
            print("  {:<12} {}".format(key, path))
        print()

        if open_report and "html" in charts:
            abs_html = os.path.abspath(charts["html"])
            webbrowser.open("file:///" + abs_html.replace(os.sep, "/"))
            print("Opened report: " + charts["html"])

    except Exception as e:
        print("Chart generation failed: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
