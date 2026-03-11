"""
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
        lines.append(f"\nTop Scorers (2023+):")
        for name, goals in scorers:
            star_tag = " ⭐" if name in stars else ""
            lines.append(f"  ⚽ {name}: {goals} goals{star_tag}")
    
    return "\n".join(lines) if lines else f"No star player data for {team}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        team = " ".join(sys.argv[1:])
    else:
        team = input("Team name: ")
    
    print(f"\n{'='*50}")
    print(f"  {team} - Player Impact Report")
    print(f"{'='*50}")
    print()
    print(get_player_summary(team))
    
    multiplier = get_team_star_impact(team)
    print(f"\nTeam attack multiplier: {multiplier:.2f}x")
    
    # Show missing player impact
    stars = STAR_PLAYERS.get(team, {})
    if stars:
        print(f"\nWhat if key players are missing?")
        for player in stars:
            if stars[player]["status"] == "active":
                without = get_team_star_impact(team, missing_players=[player])
                diff = (without - multiplier) * 100
                print(f"  Without {player}: {without:.2f}x ({diff:+.1f}%)")
