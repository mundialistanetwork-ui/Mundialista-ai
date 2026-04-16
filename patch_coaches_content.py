import re

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

# CHANGE 1: Add coaches import
if 'from coaches import' not in code:
    code = code.replace(
        '_data,\n)',
        '_data,\n)\nfrom coaches import get_coach_data'
    )

# CHANGE 2: Add coaches to analyze_match return dict
if 'home_coach' not in code:
    old = '        # Raw result (for advanced use)\n        "_raw": result,'
    new = '''        # Coaches
        "home_coach": result.get("team_a_coach", "Unknown"),
        "away_coach": result.get("team_b_coach", "Unknown"),
        "home_coach_tier": result.get("team_a_coach_tier", "Solid Organizer"),
        "away_coach_tier": result.get("team_b_coach_tier", "Solid Organizer"),
        "home_coach_style": result.get("team_a_coach_style", ""),
        "away_coach_style": result.get("team_b_coach_style", ""),
        "home_coach_atk": result.get("team_a_coach_atk", 1.0),
        "home_coach_def": result.get("team_a_coach_def", 1.0),
        "away_coach_atk": result.get("team_b_coach_atk", 1.0),
        "away_coach_def": result.get("team_b_coach_def", 1.0),
        "home_coach_honors": result.get("team_a_coach_honors", []),
        "away_coach_honors": result.get("team_b_coach_honors", []),

        # Raw result (for advanced use)
        "_raw": result,'''
    code = code.replace(old, new)

# CHANGE 3: Add coaches block to English preview
if 'COACHES MATCHUP' not in code:
    old_line = '''        f" Upset probability: {a[\'upset_prob\']:.1f}% ({a[\'underdog\']})",'''
    new_block = '''        "",
        "COACHES MATCHUP:",
        f"  {home}: {a.get('home_coach', 'Unknown')} ({a.get('home_coach_tier', 'N/A')})",
        f"    Style: {a.get('home_coach_style', 'N/A')}",
        f"    Impact: ATK x{a.get('home_coach_atk', 1.0):.3f} | DEF x{a.get('home_coach_def', 1.0):.3f}",
        f"  {away}: {a.get('away_coach', 'Unknown')} ({a.get('away_coach_tier', 'N/A')})",
        f"    Style: {a.get('away_coach_style', 'N/A')}",
        f"    Impact: ATK x{a.get('away_coach_atk', 1.0):.3f} | DEF x{a.get('away_coach_def', 1.0):.3f}",
        "",
        f" Upset probability: {a['upset_prob']:.1f}% ({a['underdog']})",'''
    code = code.replace(old_line, new_block)

with open('content_automation.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('DONE: 3 coaches patches applied to content_automation.py')
