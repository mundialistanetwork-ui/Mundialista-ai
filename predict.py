#!/usr/bin/env python
# predict.py - CLI prediction tool with chart generation
"""
Quick command-line predictions with optional chart generation.

Usage:
    python predict.py Brazil Argentina
    python predict.py Brazil Argentina --charts
    python predict.py Brazil Argentina --charts --open
    python predict.py  (interactive mode)
"""

import sys
import os
import webbrowser

from prediction_engine import predict, CONFIG
from chart_generator import generate_all_charts, generate_html_report


def print_result(result: dict):
    """Print formatted prediction result to terminal"""
    
    team_a = result['team_a']
    team_b = result['team_b']
    
    print("\n" + "="*60)
    print(f"  {team_a} vs {team_b}")
    print("="*60)
    
    # Rankings
    print(f"\n  Rankings:")
    print(f"   {team_a}: #{result['team_a_rank']} ({result['team_a_points']} pts)")
    print(f"   {team_b}: #{result['team_b_rank']} ({result['team_b_points']} pts)")
    print(f"   Gap: {result['rank_gap']} ranks")
    
    # Match Type
    print(f"\n  Match Type: {result['match_type']}")
    
    # Probabilities
    print(f"\n  Probabilities:")
    print(f"   {team_a} Win: {result['team_a_win']}%")
    print(f"   Draw:        {result['draw']}%")
    print(f"   {team_b} Win: {result['team_b_win']}%")
    
    # Expected Goals
    print(f"\n  Expected Goals:")
    print(f"   {team_a}: {result['team_a_lambda']:.2f}")
    print(f"   {team_b}: {result['team_b_lambda']:.2f}")
    
    # Star Players
    print(f"\n  Star Players:")
    stars_a = ', '.join(result['team_a_stars'][:3]) if result['team_a_stars'] else 'None tracked'
    stars_b = ', '.join(result['team_b_stars'][:3]) if result['team_b_stars'] else 'None tracked'
    boost_a = (result['team_a_star_boost'] - 1) * 100
    boost_b = (result['team_b_star_boost'] - 1) * 100
    print(f"   {team_a}: {stars_a} (+{boost_a:.0f}% boost)")
    print(f"   {team_b}: {stars_b} (+{boost_b:.0f}% boost)")
    
    # Top Scores
    print(f"\n  Most Likely Scores:")
    n_sims = result['n_simulations']
    for score, count in result['top_scores'][:5]:
        pct = 100 * count / n_sims
        print(f"   {score}: {pct:.1f}%")
    
    # Home
    if result['home']:
        print(f"\n  Home Team: {result['home']}")
    else:
        print(f"\n  Neutral Venue")
    
    print("\n" + "="*60)
    print(f"Based on {n_sims:,} Poisson simulations")
    print("="*60 + "\n")


def main():
    # Parse arguments
    args = sys.argv[1:]
    
    generate_charts = '--charts' in args or '-c' in args
    open_browser = '--open' in args or '-o' in args
    
    # Remove flags from args
    args = [a for a in args if not a.startswith('-')]
    
    # Get team names
    if len(args) >= 2:
        team_a = args[0]
        team_b = args[1]
        home = args[2] if len(args) > 2 else None
    else:
        # Interactive mode
        print("\n  MUNDIALISTA-AI - Quick Prediction")
        print("="*40)
        team_a = input("Team A: ").strip()
        team_b = input("Team B: ").strip()
        
        home_input = input("Home team (A/B/N for neutral) [N]: ").strip().upper()
        if home_input == 'A':
            home = team_a
        elif home_input == 'B':
            home = team_b
        else:
            home = None
        
        charts_input = input("Generate charts? (y/n) [n]: ").strip().lower()
        generate_charts = charts_input == 'y'
        
        if generate_charts:
            open_input = input("Open in browser? (y/n) [y]: ").strip().lower()
            open_browser = open_input != 'n'
    
    # Run prediction
    print(f"\n  Running {CONFIG['N_SIMULATIONS']:,} simulations...")
    result = predict(team_a, team_b, home=home)
    
    # Print result
    print_result(result)
    
    # Generate charts if requested
    if generate_charts:
        print("  Generating charts...")
        charts = generate_all_charts(result, save=True, show=False)
        
        # Generate HTML report
        html_path = generate_html_report(result, charts)
        
        print("\n  Charts generated!")
        print(f"     Folder: predictions_output/")
        
        # Open in browser
        if open_browser:
            print(f"\n  Opening in browser...")
            webbrowser.open('file://' + os.path.abspath(html_path))


if __name__ == "__main__":
    main()
