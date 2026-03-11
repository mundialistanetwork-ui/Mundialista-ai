print("=" * 60)
print("  UPGRADE 1/3: LAST 7 MATCHES FOR FORM")
print("=" * 60)

with open('content_automation.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Backup
with open('content_automation_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)

# Change get_team_stats call from last_n=40 to last_n=7
# The function definition
old_def = 'def get_team_stats(results, team, last_n=40):'
new_def = 'def get_team_stats(results, team, last_n=7):'

if old_def in code:
    code = code.replace(old_def, new_def)
    print("Changed default last_n from 40 to 7")
else:
    print("WARN: Could not find function definition with last_n=40")
    # Check what it currently is
    import re
    match = re.search(r'def get_team_stats\(results, team, last_n=(\d+)\)', code)
    if match:
        print(f"  Current value: last_n={match.group(1)}")

print()
print("=" * 60)
print("  UPGRADE 2/3: AUTO-UPDATE FIFA RANKINGS")
print("=" * 60)

# Create a rankings updater module
rankings_updater = '''"""
Mundialista AI - FIFA Rankings Auto-Updater
Fetches latest rankings from FIFA API or fallback sources.
Run: python update_rankings.py
"""
import pandas as pd
import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RANKINGS_CSV = os.path.join(DATA_DIR, "rankings.csv")

def fetch_rankings_from_api():
    """Try to fetch from FIFA API"""
    try:
        import urllib.request
        url = "https://www.fifa.com/fifa-world-ranking/ranking-table/men/rank/ranking.json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read())
        print(f"Fetched {len(data)} entries from FIFA API")
        return data
    except Exception as e:
        print(f"FIFA API failed: {e}")
        return None

def fetch_rankings_from_scrape():
    """Fallback: try unofficial API"""
    try:
        import urllib.request
        url = "https://raw.githubusercontent.com/martj42/international_results/master/rankings.csv"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=15)
        content = response.read().decode("utf-8")
        
        # Save raw and parse
        lines = content.strip().split("\\n")
        if len(lines) > 10:
            # Write to temp file and read with pandas
            temp_path = os.path.join(DATA_DIR, "rankings_raw.csv")
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            df = pd.read_csv(temp_path)
            print(f"Fetched {len(df)} ranking entries from GitHub source")
            
            # Get latest date only
            if "rank_date" in df.columns:
                latest_date = df["rank_date"].max()
                df = df[df["rank_date"] == latest_date]
                print(f"Latest ranking date: {latest_date}, {len(df)} teams")
            
            os.remove(temp_path)
            return df
        return None
    except Exception as e:
        print(f"GitHub scrape failed: {e}")
        return None

def update_rankings():
    """Main update function"""
    print(f"Updating FIFA rankings...")
    print(f"Current file: {RANKINGS_CSV}")
    
    if os.path.exists(RANKINGS_CSV):
        current = pd.read_csv(RANKINGS_CSV)
        print(f"Current rankings: {len(current)} teams")
        if "rank_date" in current.columns:
            print(f"Current date: {current['rank_date'].iloc[0]}")
    
    # Try sources in order
    new_data = fetch_rankings_from_scrape()
    
    if new_data is not None and isinstance(new_data, pd.DataFrame) and len(new_data) > 50:
        # Standardize columns
        col_map = {}
        for col in new_data.columns:
            cl = col.lower().strip()
            if "rank" == cl or cl == "ranking":
                col_map[col] = "rank"
            elif "country" in cl or "team" in cl or "country_full" in cl:
                col_map[col] = "country_full"
            elif "point" in cl or "total" in cl:
                col_map[col] = "total_points"
            elif "abrv" in cl or "abr" in cl or "code" in cl:
                col_map[col] = "country_abrv"
            elif "confed" in cl:
                col_map[col] = "confederation"
            elif "date" in cl:
                col_map[col] = "rank_date"
        
        new_data = new_data.rename(columns=col_map)
        
        # Ensure required columns
        for req in ["rank", "country_full", "total_points"]:
            if req not in new_data.columns:
                print(f"Missing column: {req}")
                print(f"Available: {list(new_data.columns)}")
                return False
        
        for opt in ["country_abrv", "confederation", "rank_date"]:
            if opt not in new_data.columns:
                new_data[opt] = ""
        
        new_data = new_data.sort_values("rank").reset_index(drop=True)
        
        # Backup old file
        if os.path.exists(RANKINGS_CSV):
            backup = RANKINGS_CSV.replace(".csv", "_backup.csv")
            current.to_csv(backup, index=False)
            print(f"Backup saved: {backup}")
        
        new_data.to_csv(RANKINGS_CSV, index=False)
        print(f"\\nUpdated! {len(new_data)} teams saved to {RANKINGS_CSV}")
        print(f"Top 10:")
        print(new_data.head(10)[["rank", "country_full", "total_points"]].to_string(index=False))
        return True
    else:
        print("\\nCould not fetch new rankings. Keeping current file.")
        return False

def verify_rankings():
    """Quick check that rankings are working"""
    if not os.path.exists(RANKINGS_CSV):
        print("No rankings file!")
        return False
    
    df = pd.read_csv(RANKINGS_CSV)
    print(f"\\nVerification:")
    print(f"  Teams: {len(df)}")
    print(f"  Rank range: {df['rank'].min()} - {df['rank'].max()}")
    
    # Check key teams
    key_teams = ["Argentina", "Brazil", "France", "Germany", "Mexico", "Bolivia", "Suriname"]
    for team in key_teams:
        row = df[df["country_full"] == team]
        if len(row) > 0:
            print(f"  {team}: rank={row.iloc[0]['rank']}, pts={row.iloc[0]['total_points']:.0f}")
        else:
            print(f"  {team}: NOT FOUND")
    
    return True

if __name__ == "__main__":
    import sys
    if "--verify" in sys.argv:
        verify_rankings()
    else:
        success = update_rankings()
        verify_rankings()
        if success:
            print("\\nDone! Rankings updated successfully.")
        else:
            print("\\nUsing existing rankings.")
'''

with open('update_rankings.py', 'w', encoding='utf-8') as f:
    f.write(rankings_updater)
print("Created update_rankings.py")

print()
print("=" * 60)
print("  UPGRADE 3/3: PLAYER IMPACT SYSTEM")
print("=" * 60)

# Create player impact module
player_impact = '''"""
Mundialista AI - Player Impact System
Factors in key player availability and quality.
"""
import pandas as pd
import os
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Star player impact multipliers
# These players significantly affect their team performance
STAR_PLAYERS = {
    "Argentina": {
        "Lionel Messi": {"attack": 1.15, "status": "active"},
        "Lautaro Martínez": {"attack": 1.08, "status": "active"},
        "Julián Álvarez": {"attack": 1.05, "status": "active"},
    },
    "France": {
        "Kylian Mbappé": {"attack": 1.15, "status": "active"},
        "Antoine Griezmann": {"attack": 1.06, "status": "retired_intl"},
        "Olivier Giroud": {"attack": 1.04, "status": "retired_intl"},
    },
    "Brazil": {
        "Vinícius Júnior": {"attack": 1.12, "status": "active"},
        "Raphinha": {"attack": 1.06, "status": "active"},
        "Rodrygo": {"attack": 1.05, "status": "active"},
    },
    "Portugal": {
        "Cristiano Ronaldo": {"attack": 1.10, "status": "active"},
        "Bruno Fernandes": {"attack": 1.07, "status": "active"},
        "Bernardo Silva": {"attack": 1.05, "status": "active"},
    },
    "England": {
        "Harry Kane": {"attack": 1.12, "status": "active"},
        "Bukayo Saka": {"attack": 1.08, "status": "active"},
        "Jude Bellingham": {"attack": 1.08, "status": "active"},
    },
    "Germany": {
        "Florian Wirtz": {"attack": 1.10, "status": "active"},
        "Kai Havertz": {"attack": 1.06, "status": "active"},
        "Jamal Musiala": {"attack": 1.08, "status": "active"},
    },
    "Spain": {
        "Lamine Yamal": {"attack": 1.10, "status": "active"},
        "Álvaro Morata": {"attack": 1.05, "status": "active"},
        "Dani Olmo": {"attack": 1.06, "status": "active"},
    },
    "Netherlands": {
        "Cody Gakpo": {"attack": 1.08, "status": "active"},
        "Memphis Depay": {"attack": 1.05, "status": "active"},
    },
    "Belgium": {
        "Romelu Lukaku": {"attack": 1.08, "status": "active"},
        "Kevin De Bruyne": {"attack": 1.10, "status": "active"},
    },
    "Colombia": {
        "Luis Díaz": {"attack": 1.08, "status": "active"},
        "James Rodríguez": {"attack": 1.05, "status": "active"},
    },
    "Uruguay": {
        "Darwin Núñez": {"attack": 1.08, "status": "active"},
        "Federico Valverde": {"attack": 1.06, "status": "active"},
    },
    "Croatia": {
        "Luka Modrić": {"attack": 1.06, "status": "active"},
    },
    "Norway": {
        "Erling Haaland": {"attack": 1.18, "status": "active"},
        "Martin Ødegaard": {"attack": 1.08, "status": "active"},
    },
    "Egypt": {
        "Mohamed Salah": {"attack": 1.12, "status": "active"},
    },
    "South Korea": {
        "Son Heung-min": {"attack": 1.12, "status": "active"},
    },
    "Japan": {
        "Takefusa Kubo": {"attack": 1.06, "status": "active"},
        "Kaoru Mitoma": {"attack": 1.06, "status": "active"},
    },
    "United States": {
        "Christian Pulisic": {"attack": 1.08, "status": "active"},
        "Weston McKennie": {"attack": 1.04, "status": "active"},
    },
    "Mexico": {
        "Raúl Jiménez": {"attack": 1.06, "status": "active"},
    },
    "Senegal": {
        "Sadio Mané": {"attack": 1.10, "status": "active"},
    },
    "Morocco": {
        "Hakim Ziyech": {"attack": 1.07, "status": "active"},
        "Achraf Hakimi": {"attack": 1.05, "status": "active"},
    },
    "Italy": {
        "Federico Chiesa": {"attack": 1.06, "status": "active"},
    },
}

def get_team_star_impact(team, missing_players=None):
    """
    Calculate attack multiplier based on available star players.
    
    Args:
        team: Team name
        missing_players: List of player names who are injured/unavailable
    
    Returns:
        float: Attack multiplier (1.0 = no impact, >1.0 = boost)
    """
    if team not in STAR_PLAYERS:
        return 1.0
    
    if missing_players is None:
        missing_players = []
    
    missing_lower = [p.lower() for p in missing_players]
    
    total_boost = 0.0
    active_count = 0
    
    for player, info in STAR_PLAYERS[team].items():
        if info["status"] != "active":
            continue
        
        player_boost = info["attack"] - 1.0  # e.g., 1.15 -> 0.15
        
        if player.lower() in missing_lower:
            # Player missing = lose their boost AND a penalty
            total_boost -= player_boost * 0.5  # penalty for missing star
        else:
            total_boost += player_boost
            active_count += 1
    
    # Cap the total boost
    multiplier = 1.0 + min(total_boost, 0.20)  # max 20% team boost
    multiplier = max(multiplier, 0.85)  # max 15% penalty
    
    return multiplier

def get_top_scorers(team, n=5):
    """Get top recent scorers for a team from goalscorers data"""
    try:
        goalscorers_path = os.path.join(DATA_DIR, "goalscorers.csv")
        if not os.path.exists(goalscorers_path):
            return []
        
        df = pd.read_csv(goalscorers_path)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        
        # Last 2 years
        recent = df[df["date"] >= "2023-01-01"]
        team_goals = recent[recent["team"] == team]
        
        if len(team_goals) == 0:
            return []
        
        top = team_goals["scorer"].value_counts().head(n)
        return [(name, goals) for name, goals in top.items()]
    except Exception:
        return []

def get_player_summary(team):
    """Get a formatted summary of key players for a team"""
    stars = STAR_PLAYERS.get(team, {})
    scorers = get_top_scorers(team)
    
    lines = []
    if stars:
        active = [(p, i) for p, i in stars.items() if i["status"] == "active"]
        lines.append(f"Star Players ({len(active)} active):")
        for player, info in active:
            boost_pct = (info["attack"] - 1) * 100
            lines.append(f"  ⭐ {player} (+{boost_pct:.0f}% attack)")
    
    if scorers:
        lines.append(f"\\nTop Scorers (2023+):")
        for name, goals in scorers:
            star_tag = " ⭐" if name in stars else ""
            lines.append(f"  ⚽ {name}: {goals} goals{star_tag}")
    
    return "\\n".join(lines) if lines else f"No star player data for {team}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        team = " ".join(sys.argv[1:])
    else:
        team = input("Team name: ")
    
    print(f"\\n{'='*50}")
    print(f"  {team} - Player Impact Report")
    print(f"{'='*50}")
    print()
    print(get_player_summary(team))
    
    multiplier = get_team_star_impact(team)
    print(f"\\nTeam attack multiplier: {multiplier:.2f}x")
    
    # Show missing player impact
    stars = STAR_PLAYERS.get(team, {})
    if stars:
        print(f"\\nWhat if key players are missing?")
        for player in stars:
            if stars[player]["status"] == "active":
                without = get_team_star_impact(team, missing_players=[player])
                diff = (without - multiplier) * 100
                print(f"  Without {player}: {without:.2f}x ({diff:+.1f}%)")
'''

with open('player_impact.py', 'w', encoding='utf-8') as f:
    f.write(player_impact)
print("Created player_impact.py")

# Now integrate player impact into content_automation.py
print("\nIntegrating player impact into predictions...")

# Add import
if 'from player_impact import' not in code:
    code = code.replace(
        'from data_loader import get_team_ranking',
        'from data_loader import get_team_ranking\\nfrom player_impact import get_team_star_impact'
    )
    print("Added player_impact import")

# Add player impact after ranking adjustment, before Poisson simulation
old_apply_home = '    # Apply home advantage\n    home_lambda = max(0.3, home_blend * 1.08)\n    away_lambda = max(0.3, away_blend * 0.92)'

new_apply_home = '''    # Apply star player impact
    home_star = get_team_star_impact(home_team)
    away_star = get_team_star_impact(away_team)
    home_blend *= home_star
    away_blend *= away_star
    # Apply home advantage
    home_lambda = max(0.3, home_blend * 1.08)
    away_lambda = max(0.3, away_blend * 0.92)'''

if old_apply_home in code:
    code = code.replace(old_apply_home, new_apply_home)
    print("Integrated star player impact into lambda calculation")
else:
    print("WARN: Could not find home advantage block")
    # Try to find it
    if 'home_blend * 1.08' in code:
        print("  Found home_blend * 1.08 - checking context...")

with open('content_automation.py', 'w', encoding='utf-8') as f:
    f.write(code)

# Verify syntax
import py_compile
try:
    py_compile.compile('content_automation.py', doraise=True)
    py_compile.compile('player_impact.py', doraise=True)
    py_compile.compile('update_rankings.py', doraise=True)
    print("\nALL SYNTAX CHECKS: OK")
except py_compile.PyCompileError as e:
    print(f"\nSYNTAX ERROR: {e}")
    with open('content_automation_backup.py', 'r', encoding='utf-8') as f:
        backup = f.read()
    with open('content_automation.py', 'w', encoding='utf-8') as f:
        f.write(backup)
    print("Backup restored!")
    exit()

# Test everything
print("\n" + "=" * 60)
print("  TESTING ALL UPGRADES")
print("=" * 60)

import sys
for mod in list(sys.modules.keys()):
    if 'content' in mod or 'data_loader' in mod or 'strength' in mod or 'player' in mod:
        del sys.modules[mod]

from content_automation import quick_simulate
from player_impact import get_team_star_impact, get_player_summary

# Test player impact
print("\nPlayer Impact Test:")
for team in ['Argentina', 'Norway', 'Bolivia']:
    mult = get_team_star_impact(team)
    print(f"  {team}: {mult:.2f}x attack boost")

# Test predictions
print("\nPrediction Test (with all upgrades):")
tests = [
    ('Argentina', 'Brazil', 'Close match'),
    ('France', 'England', 'France slight edge'),
    ('Bolivia', 'Suriname', 'Bolivia wins'),
    ('Brazil', 'India', 'Brazil dominates'),
    ('Norway', 'San Marino', 'Norway crushes (Haaland!)'),
    ('France', 'San Marino', 'France crushes'),
]

print(f"  {'Matchup':<30s} {'Home':>6s} {'Draw':>6s} {'Away':>6s}")
print("  " + "-" * 55)
for home, away, note in tests:
    r = quick_simulate(home, away)
    hw = r['home_win_pct']
    d = r['draw_pct']
    aw = r['away_win_pct']
    print(f"  {home+' v '+away:<30s} {hw:5.1f}% {d:5.1f}% {aw:5.1f}%  ({note})")

print("\n" + "=" * 60)
print("  ALL UPGRADES COMPLETE!")
print("=" * 60)
print("  New commands:")
print("    python predict.py Brazil Argentina")
print("    python player_impact.py Argentina")
print("    python update_rankings.py")
print("    python update_rankings.py --verify")
print("    python diagnostics.py")
