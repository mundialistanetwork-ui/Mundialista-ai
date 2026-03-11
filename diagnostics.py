import sys
import os
import traceback
from datetime import datetime

print("=" * 70)
print("  MUNDIALISTA-AI UNIVERSAL DIAGNOSTICS & CALIBRATOR")
print(f"  Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

score = 0
total = 0
issues = []

# ============================================================
# SECTION 1: CORE MODULES
# ============================================================
print("\n[1/7] CORE MODULES")
print("-" * 40)

modules = [
    'data_loader', 'content_automation',
    'pandas', 'numpy', 'scipy'
]
for mod in modules:
    total += 1
    try:
        __import__(mod)
        print(f"  OK  {mod}")
        score += 1
    except ImportError as e:
        print(f"  FAIL  {mod}: {e}")
        issues.append(f"Module {mod} missing")

# ============================================================
# SECTION 2: DATA FILES
# ============================================================
print("\n[2/7] DATA FILES")
print("-" * 40)

data_files = [
    'data/results.csv',
    'data/goalscorers.csv',
    'data/rankings.csv',
    'data/shootouts.csv',
]
for f in data_files:
    total += 1
    if os.path.exists(f):
        size = os.path.getsize(f) / 1024
        print(f"  OK  {f} ({size:.0f} KB)")
        score += 1
    else:
        # Try alternate paths
        alt = f.replace('data/', '')
        if os.path.exists(alt):
            size = os.path.getsize(alt) / 1024
            print(f"  WARN  {f} not found, but {alt} exists ({size:.0f} KB)")
            issues.append(f"{f} in wrong location")
            score += 0.5
        else:
            print(f"  FAIL  {f} NOT FOUND")
            issues.append(f"Missing {f}")

# ============================================================
# SECTION 3: DATA LOADING
# ============================================================
print("\n[3/7] DATA LOADING")
print("-" * 40)

results = None
rankings = None
goalscorers = None

try:
    from data_loader import load_results
    results = load_results()
    total += 1
    if results is not None and len(results) > 0:
        print(f"  OK  Results: {len(results)} matches loaded")
        
        # Check date range
        import pandas as pd
        if isinstance(results, pd.DataFrame):
            if 'date' in results.columns:
                results['date'] = pd.to_datetime(results['date'], errors='coerce')
                min_date = results['date'].min()
                max_date = results['date'].max()
                print(f"       Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
            
            # Count unique teams
            teams_home = set(results['home_team'].unique()) if 'home_team' in results.columns else set()
            teams_away = set(results['away_team'].unique()) if 'away_team' in results.columns else set()
            all_teams = teams_home | teams_away
            print(f"       Unique teams: {len(all_teams)}")
            
            # Tournament types
            if 'tournament' in results.columns:
                top_tournaments = results['tournament'].value_counts().head(5)
                print(f"       Top tournaments:")
                for t, c in top_tournaments.items():
                    print(f"         {t}: {c} matches")
        score += 1
    else:
        print(f"  FAIL  Results empty or None")
        issues.append("Results not loading")
except Exception as e:
    total += 1
    print(f"  FAIL  Results: {e}")
    issues.append(f"Results error: {e}")

try:
    from data_loader import load_rankings
    rankings = load_rankings()
    total += 1
    import pandas as pd
    if isinstance(rankings, pd.DataFrame) and len(rankings) > 0:
        print(f"  OK  Rankings: {len(rankings)} entries")
        print(f"       Columns: {list(rankings.columns)}")
        score += 1
    elif rankings is None:
        print(f"  FAIL  Rankings returned None")
        issues.append("Rankings returning None")
    else:
        print(f"  WARN  Rankings: type={type(rankings)}, len={len(rankings) if hasattr(rankings, '__len__') else '?'}")
        issues.append("Rankings format unexpected")
        score += 0.5
except Exception as e:
    total += 1
    print(f"  FAIL  Rankings: {e}")
    issues.append(f"Rankings error: {e}")

try:
    from data_loader import load_goalscorers
    goalscorers = load_goalscorers()
    total += 1
    import pandas as pd
    if isinstance(goalscorers, pd.DataFrame) and len(goalscorers) > 0:
        print(f"  OK  Goalscorers: {len(goalscorers)} entries")
        print(f"       Columns: {list(goalscorers.columns)}")
        
        # Top scorers recent
        if 'date' in goalscorers.columns and 'scorer' in goalscorers.columns:
            goalscorers['date'] = pd.to_datetime(goalscorers['date'], errors='coerce')
            recent = goalscorers[goalscorers['date'] >= '2023-01-01']
            if len(recent) > 0:
                top = recent['scorer'].value_counts().head(10)
                print(f"       Top scorers (2023+):")
                for name, goals in top.items():
                    # Find their team
                    team = recent[recent['scorer'] == name]['team'].mode()
                    team_str = team.iloc[0] if len(team) > 0 else '?'
                    print(f"         {name} ({team_str}): {goals} goals")
        score += 1
    else:
        print(f"  FAIL  Goalscorers empty or None")
        issues.append("Goalscorers not loading")
except Exception as e:
    total += 1
    print(f"  FAIL  Goalscorers: {e}")
    issues.append(f"Goalscorers error: {e}")

# ============================================================
# SECTION 4: FIFA RANKINGS CHECK
# ============================================================
print("\n[4/7] FIFA RANKINGS INTEGRITY")
print("-" * 40)

from data_loader import get_team_ranking

test_teams_expected = {
    'Brazil': (1, 15),
    'Argentina': (1, 10),
    'France': (1, 12),
    'Germany': (10, 25),
    'Mexico': (10, 30),
    'United States': (10, 30),
    'Bolivia': (60, 110),
    'Suriname': (120, 180),
    'India': (90, 150),
    'Iceland': (50, 90),
    'San Marino': (190, 211),
}

rankings_ok = 0
rankings_total = 0
for team, (exp_low, exp_high) in test_teams_expected.items():
    rankings_total += 1
    try:
        r = get_team_ranking(team)
        if isinstance(r, dict):
            rank = r.get('rank', r.get('ranking', None))
            pts = r.get('total_points', r.get('points', None))
        else:
            rank = r
            pts = None
        
        if rank and rank != 100:  # 100 is the suspected default
            in_range = exp_low <= rank <= exp_high
            status = "OK" if in_range else "DRIFT"
            pts_str = f", pts={pts:.0f}" if pts else ""
            print(f"  {status:5s}  {team}: rank={rank}{pts_str} (expected {exp_low}-{exp_high})")
            if in_range:
                rankings_ok += 1
            else:
                rankings_ok += 0.5
        else:
            print(f"  FAIL  {team}: rank={rank} (DEFAULT - not real!)")
            issues.append(f"Ranking default for {team}")
    except Exception as e:
        print(f"  FAIL  {team}: {e}")
        issues.append(f"Ranking error for {team}")

total += 1
if rankings_ok == rankings_total:
    print(f"\n  Rankings: {rankings_ok}/{rankings_total} correct")
    score += 1
elif rankings_ok > 0:
    print(f"\n  Rankings: {rankings_ok}/{rankings_total} correct")
    score += 0.5
else:
    print(f"\n  Rankings: COMPLETELY BROKEN (all defaults)")
    issues.append("FIFA Rankings completely broken")

# ============================================================
# SECTION 5: PREDICTION CALIBRATION
# ============================================================
print("\n[5/7] PREDICTION CALIBRATION")
print("-" * 40)

calibration_matches = [
    # (home, away, expected_winner, min_win_pct)
    ('Brazil', 'India', 'home', 70),
    ('Argentina', 'Suriname', 'home', 75),
    ('Mexico', 'Iceland', 'home', 55),
    ('Bolivia', 'Suriname', 'home', 50),
    ('France', 'San Marino', 'home', 85),
    ('Germany', 'United States', 'home', 45),
    ('Brazil', 'Argentina', 'either', 25),  # Close match
]

cal_ok = 0
cal_total = 0

try:
    from content_automation import quick_simulate
    
    for home, away, expected, min_pct in calibration_matches:
        cal_total += 1
        try:
            r = quick_simulate(home, away)
            hw = r.get('home_win_pct', 0)
            d = r.get('draw_pct', 0)
            aw = r.get('away_win_pct', 0)
            
            if expected == 'home':
                correct = hw > aw and hw >= min_pct * 0.5  # At least half expected
                reasonable = hw > aw
            elif expected == 'away':
                correct = aw > hw and aw >= min_pct * 0.5
                reasonable = aw > hw
            else:  # either - close match
                correct = abs(hw - aw) < 30
                reasonable = True
            
            if correct:
                status = "OK"
                cal_ok += 1
            elif reasonable:
                status = "WEAK"
                cal_ok += 0.5
            else:
                status = "WRONG"
            
            winner = home if hw > aw else away
            print(f"  {status:5s}  {home} vs {away}: {hw:.1f}%-{d:.1f}%-{aw:.1f}% (favors {winner})")
            
            if status == "WRONG":
                issues.append(f"WRONG prediction: {home} vs {away} should favor {expected}")
                
        except Exception as e:
            print(f"  FAIL  {home} vs {away}: {e}")
            issues.append(f"Prediction error: {home} vs {away}")
    
    total += 1
    if cal_ok >= cal_total * 0.7:
        score += 1
    elif cal_ok >= cal_total * 0.4:
        score += 0.5

except Exception as e:
    total += 1
    print(f"  FAIL  Could not run predictions: {e}")
    traceback.print_exc()
    issues.append(f"Prediction system error: {e}")

# ============================================================
# SECTION 6: KEY PLAYERS DATA
# ============================================================
print("\n[6/7] KEY PLAYERS DATA")
print("-" * 40)

import pandas as pd

if goalscorers is not None and isinstance(goalscorers, pd.DataFrame):
    print(f"  Columns: {list(goalscorers.columns)}")
    
    # Check what player data we have
    has_scorer = 'scorer' in goalscorers.columns
    has_team = 'team' in goalscorers.columns
    has_minute = 'minute' in goalscorers.columns
    has_own_goal = 'own_goal' in goalscorers.columns
    has_penalty = 'penalty' in goalscorers.columns
    
    print(f"  Has scorer names: {has_scorer}")
    print(f"  Has team: {has_team}")
    print(f"  Has minute: {has_minute}")
    print(f"  Has own_goal flag: {has_own_goal}")
    print(f"  Has penalty flag: {has_penalty}")
    
    total += 1
    if has_scorer and has_team:
        score += 1
        
        # Key players check - are star players in the data?
        star_players = [
            ('Lionel Messi', 'Argentina'),
            ('Kylian Mbappé', 'France'),
            ('Kylian Mbappe', 'France'),
            ('Cristiano Ronaldo', 'Portugal'),
            ('Erling Haaland', 'Norway'),
            ('Vinicius Junior', 'Brazil'),
            ('Vinicius Júnior', 'Brazil'),
            ('Harry Kane', 'England'),
            ('Lautaro Martinez', 'Argentina'),
            ('Lautaro Martínez', 'Argentina'),
        ]
        
        print(f"\n  Star Players Check:")
        for player, team in star_players:
            found = goalscorers[goalscorers['scorer'].str.contains(player, case=False, na=False)]
            if len(found) > 0:
                recent = found[found['date'] >= '2023-01-01'] if 'date' in found.columns else found
                print(f"    OK  {player} ({team}): {len(found)} total goals, {len(recent)} since 2023")
            # Don't print NOT FOUND for accent variations
            elif 'é' not in player and 'í' not in player:
                print(f"    --  {player} ({team}): not found")
        
        # Top scorers by team for key nations
        print(f"\n  Top Scorers by Nation (2022+):")
        key_nations = ['Argentina', 'Brazil', 'France', 'Germany', 'England', 'Mexico', 'United States']
        goalscorers['date'] = pd.to_datetime(goalscorers['date'], errors='coerce')
        recent_gs = goalscorers[goalscorers['date'] >= '2022-01-01']
        
        for nation in key_nations:
            nation_goals = recent_gs[recent_gs['team'] == nation]
            if len(nation_goals) > 0:
                top3 = nation_goals['scorer'].value_counts().head(3)
                players_str = ", ".join([f"{name}({g})" for name, g in top3.items()])
                print(f"    {nation}: {players_str}")
            else:
                print(f"    {nation}: no goals data")
    else:
        issues.append("Goalscorers missing key columns")
else:
    total += 1
    print(f"  FAIL  No goalscorers data available")
    issues.append("No goalscorers data")

# ============================================================
# SECTION 7: SIMULATION ENGINE CHECK
# ============================================================
print("\n[7/7] SIMULATION ENGINE")
print("-" * 40)

try:
    import content_automation as simulation_engine
    total += 1
    
    # Check what functions exist
    sim_funcs = [f for f in dir(simulation_engine) if not f.startswith('_') and callable(getattr(simulation_engine, f))]
    print(f"  Functions: {', '.join(sim_funcs)}")
    
    # Check if Poisson-based
    import inspect
    source = inspect.getsource(simulation_engine)
    has_poisson = 'poisson' in source.lower()
    has_monte_carlo = 'monte' in source.lower() or 'simul' in source.lower()
    has_elo = 'elo' in source.lower()
    has_ranking = 'rank' in source.lower()
    
    print(f"  Uses Poisson: {has_poisson}")
    print(f"  Uses Monte Carlo: {has_monte_carlo}")
    print(f"  Uses Elo/Rating: {has_elo}")
    print(f"  Uses Rankings: {has_ranking}")
    score += 1
    
except Exception as e:
    total += 1
    print(f"  FAIL  {e}")
    issues.append(f"Simulation engine error: {e}")

# ============================================================
# FINAL REPORT
# ============================================================
pct = (score / total * 100) if total > 0 else 0

print("\n" + "=" * 70)
print(f"  HEALTH SCORE: {score:.1f}/{total} ({pct:.0f}%)")
print("=" * 70)

if pct >= 90:
    grade = "A - EXCELLENT"
elif pct >= 75:
    grade = "B - GOOD (minor issues)"
elif pct >= 50:
    grade = "C - NEEDS WORK"
elif pct >= 25:
    grade = "D - SERIOUS ISSUES"
else:
    grade = "F - CRITICAL"

print(f"  GRADE: {grade}")

if issues:
    print(f"\n  ISSUES FOUND ({len(issues)}):")
    for i, issue in enumerate(issues, 1):
        print(f"    {i}. {issue}")

print()
if 'Rankings completely broken' in str(issues) or 'default' in str(issues).lower():
    print("  >>> PRIORITY FIX: FIFA Rankings are returning defaults!")
    print("      This is why weak teams appear as strong as Brazil.")
    print("      Fix rankings loading in data_loader.py first!")
elif any('WRONG' in i for i in issues):
    print("  >>> PRIORITY FIX: Prediction calibration failing!")
    print("      Some matchups are producing inverted results.")
else:
    print("  System looks healthy! Ready for predictions.")

print("=" * 70)
