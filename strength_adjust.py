"""
Opponent-Strength Adjustment Module
====================================
Adjusts team stats based on quality of opponents faced.

Bolivia losing 0-3 to Argentina counts differently than
Suriname beating Anguilla 4-0.

Uses iterative rating system similar to simplified Elo.
"""
import numpy as np
import pandas as pd
from data_loader import load_results


def compute_team_ratings(results, iterations=5):
    """
    Compute strength rating for every team using iterative method.
    
    Start: every team rated 1.0
    Each iteration: rating = weighted average of results adjusted by opponent rating
    After 5 iterations, ratings stabilize.
    
    Returns dict: {team_name: rating}
    """
    all_teams = sorted(set(results['home_team'].unique()) | set(results['away_team'].unique()))
    ratings = {t: 1.0 for t in all_teams}
    
    for iteration in range(iterations):
        new_ratings = {}
        for team in all_teams:
            # Get all matches for this team
            home = results[results['home_team'] == team]
            away = results[results['away_team'] == team]
            
            weighted_scores = []
            
            for _, r in home.iterrows():
                opp = r['away_team']
                opp_rating = ratings.get(opp, 1.0)
                gf = r['home_score']
                ga = r['away_score']
                # Goal difference weighted by opponent strength
                # Scoring 2 vs Brazil (rating 1.8) worth more than 2 vs Anguilla (rating 0.3)
                match_score = (gf - ga) * opp_rating
                weighted_scores.append(match_score)
            
            for _, r in away.iterrows():
                opp = r['home_team']
                opp_rating = ratings.get(opp, 1.0)
                gf = r['away_score']
                ga = r['home_score']
                match_score = (gf - ga) * opp_rating
                weighted_scores.append(match_score)
            
            if len(weighted_scores) > 0:
                avg_weighted = np.mean(weighted_scores)
                # Convert to positive scale centered around 1.0
                # Clamp between 0.2 and 3.0
                new_rating = max(0.2, min(3.0, 1.0 + avg_weighted / 3.0))
            else:
                new_rating = 1.0
            
            new_ratings[team] = new_rating
        
        ratings = new_ratings
    
    return ratings


def get_adjusted_stats(results, team, ratings, last_n=40):
    """
    Get team stats adjusted for opponent strength.
    
    Instead of raw avg_gf, we compute:
    - adjusted_gf: goals scored weighted UP when scored against strong teams
    - adjusted_ga: goals conceded weighted DOWN when conceded against strong teams
    """
    home = results[results['home_team'] == team]
    away = results[results['away_team'] == team]
    
    matches = []
    for _, r in home.iterrows():
        matches.append({
            'date': r['date'],
            'gf': int(r['home_score']),
            'ga': int(r['away_score']),
            'opponent': r['away_team'],
            'opp_rating': ratings.get(r['away_team'], 1.0),
        })
    for _, r in away.iterrows():
        matches.append({
            'date': r['date'],
            'gf': int(r['away_score']),
            'ga': int(r['home_score']),
            'opponent': r['home_team'],
            'opp_rating': ratings.get(r['home_team'], 1.0),
        })
    
    matches.sort(key=lambda x: str(x['date']))
    matches = matches[-last_n:]
    
    if len(matches) == 0:
        return None
    
    # Raw stats
    raw_gf = np.mean([m['gf'] for m in matches])
    raw_ga = np.mean([m['ga'] for m in matches])
    
    # Adjusted stats
    # When you score against a strong team, your goals are worth more
    # When you concede against a strong team, it's less bad
    # Formula: adjusted_gf = sum(gf * opp_rating) / sum(opp_rating)
    # This means scoring 1 vs Brazil (1.8) = scoring 1.8 vs average (1.0)
    
    total_opp_rating = sum(m['opp_rating'] for m in matches)
    
    adj_gf = sum(m['gf'] * m['opp_rating'] for m in matches) / total_opp_rating
    # For goals against: conceding vs strong team is more expected (less bad)
    # So we DIVIDE by opp_rating: conceding 3 vs Argentina (1.8) = conceding 1.67 vs average
    adj_ga = sum(m['ga'] / m['opp_rating'] for m in matches) / len(matches)
    
    # Blend: 60% adjusted, 40% raw (don't fully trust the adjustment)
    blend = 0.6
    blended_gf = blend * adj_gf + (1 - blend) * raw_gf
    blended_ga = blend * adj_ga + (1 - blend) * raw_ga
    
    return {
        'raw_gf': raw_gf,
        'raw_ga': raw_ga,
        'adj_gf': adj_gf,
        'adj_ga': adj_ga,
        'blended_gf': blended_gf,
        'blended_ga': blended_ga,
        'n_matches': len(matches),
        'team_rating': ratings.get(team, 1.0),
        'avg_opp_rating': np.mean([m['opp_rating'] for m in matches]),
    }


def print_ratings_table(ratings, top_n=30):
    """Print top and bottom rated teams."""
    ranked = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nTOP {top_n} TEAMS BY STRENGTH RATING:")
    print("=" * 50)
    print(f"  {'Rank':<6s} {'Team':<30s} {'Rating':>8s}")
    print("  " + "-" * 44)
    for i, (team, rating) in enumerate(ranked[:top_n], 1):
        bar = "#" * int(rating * 10)
        print(f"  {i:<6d} {team:<30s} {rating:>7.3f}  {bar}")
    
    print(f"\nBOTTOM {top_n} TEAMS:")
    print("  " + "-" * 44)
    for i, (team, rating) in enumerate(ranked[-top_n:], len(ranked) - top_n + 1):
        bar = "#" * int(rating * 10)
        print(f"  {i:<6d} {team:<30s} {rating:>7.3f}  {bar}")


def compare_teams(results, ratings, team_a, team_b):
    """Compare two teams with adjusted stats."""
    stats_a = get_adjusted_stats(results, team_a, ratings)
    stats_b = get_adjusted_stats(results, team_b, ratings)
    
    if stats_a is None:
        print(f"{team_a}: NO DATA")
        return
    if stats_b is None:
        print(f"{team_b}: NO DATA")
        return
    
    print(f"\n{'=' * 70}")
    print(f"  ADJUSTED COMPARISON: {team_a} vs {team_b}")
    print(f"{'=' * 70}")
    print()
    print(f"  {'Metric':<30s} {team_a:>15s} {team_b:>15s}")
    print(f"  {'-' * 60}")
    print(f"  {'Team Rating':<30s} {stats_a['team_rating']:>15.3f} {stats_b['team_rating']:>15.3f}")
    print(f"  {'Avg Opponent Rating':<30s} {stats_a['avg_opp_rating']:>15.3f} {stats_b['avg_opp_rating']:>15.3f}")
    print(f"  {'Matches':<30s} {stats_a['n_matches']:>15d} {stats_b['n_matches']:>15d}")
    print()
    print(f"  {'Raw Goals For':<30s} {stats_a['raw_gf']:>15.2f} {stats_b['raw_gf']:>15.2f}")
    print(f"  {'Raw Goals Against':<30s} {stats_a['raw_ga']:>15.2f} {stats_b['raw_ga']:>15.2f}")
    print(f"  {'Raw Goal Diff':<30s} {stats_a['raw_gf']-stats_a['raw_ga']:>+15.2f} {stats_b['raw_gf']-stats_b['raw_ga']:>+15.2f}")
    print()
    print(f"  {'Adjusted Goals For':<30s} {stats_a['adj_gf']:>15.2f} {stats_b['adj_gf']:>15.2f}")
    print(f"  {'Adjusted Goals Against':<30s} {stats_a['adj_ga']:>15.2f} {stats_b['adj_ga']:>15.2f}")
    print(f"  {'Adjusted Goal Diff':<30s} {stats_a['adj_gf']-stats_a['adj_ga']:>+15.2f} {stats_b['adj_gf']-stats_b['adj_ga']:>+15.2f}")
    print()
    print(f"  {'BLENDED Goals For (60/40)':<30s} {stats_a['blended_gf']:>15.2f} {stats_b['blended_gf']:>15.2f}")
    print(f"  {'BLENDED Goals Against':<30s} {stats_a['blended_ga']:>15.2f} {stats_b['blended_ga']:>15.2f}")
    print(f"  {'BLENDED Goal Diff':<30s} {stats_a['blended_gf']-stats_a['blended_ga']:>+15.2f} {stats_b['blended_gf']-stats_b['blended_ga']:>+15.2f}")
    print()
    
    # Who SHOULD win?
    a_strength = stats_a['blended_gf'] - stats_a['blended_ga']
    b_strength = stats_b['blended_gf'] - stats_b['blended_ga']
    
    if a_strength > b_strength + 0.3:
        print(f"  VERDICT: {team_a} should be favored")
    elif b_strength > a_strength + 0.3:
        print(f"  VERDICT: {team_b} should be favored")
    else:
        print(f"  VERDICT: Very close matchup!")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    import sys
    
    print("Loading match data...")
    results = load_results()
    print(f"Loaded {len(results):,} matches")
    
    print("Computing strength ratings (5 iterations)...")
    ratings = compute_team_ratings(results)
    print("Done!")
    
    if len(sys.argv) >= 3:
        # Compare two teams: python strength_adjust.py Bolivia Suriname
        team_a = sys.argv[1]
        team_b = sys.argv[2]
        
        # Fuzzy match
        all_teams = list(ratings.keys())
        for orig in [team_a, team_b]:
            found = [t for t in all_teams if orig.lower() in t.lower()]
            if found:
                if orig == team_a:
                    team_a = found[0]
                else:
                    team_b = found[0]
        
        compare_teams(results, ratings, team_a, team_b)
    
    elif len(sys.argv) == 2 and sys.argv[1] == "rankings":
        print_ratings_table(ratings, top_n=30)
    
    else:
        print()
        print("USAGE:")
        print("  python strength_adjust.py Bolivia Suriname    (compare two teams)")
        print("  python strength_adjust.py rankings            (show all ratings)")
        print()
        # Default: show rankings
        print_ratings_table(ratings, top_n=20)