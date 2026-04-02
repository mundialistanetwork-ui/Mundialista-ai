import math

# --- Manual Key Player Database ---
MANUAL_KEY_PLAYERS = {
    # France
    "Mbappe": {"attack": 1.15, "status": "active"},
    "Griezmann": {"attack": 1.08, "status": "active"},
    # Argentina
    "Messi": {"attack": 1.12, "status": "active"},
    # England
    "Kane": {"attack": 1.10, "status": "active"},
    "Bellingham": {"attack": 1.08, "status": "active"},
    # Brazil
    "Vinicius Jr": {"attack": 1.10, "status": "active"},
    "Rodrygo": {"attack": 1.05, "status": "active"},
    # Portugal
    "Ronaldo": {"attack": 1.05, "status": "active"},
    "Bruno Fernandes": {"attack": 1.07, "status": "active"},
}

def get_team_key_players(team_name):
    team_lower = team_name.lower()
    team_map = {
        "france": ["Mbappe", "Griezmann"],
        "argentina": ["Messi"],
        "england": ["Kane", "Bellingham"],
        "brazil": ["Vinicius Jr", "Rodrygo"],
        "portugal": ["Ronaldo", "Bruno Fernandes"]
    }
    return team_map.get(team_lower, [])

def calculate_squad_depth_boost(team_name):
    key_players = get_team_key_players(team_name)
    total_boost = 1.0
    weights = [1.0, 0.75, 0.5, 0.35, 0.25, 0.15]

    for i, player_name in enumerate(key_players[:6]):
        player_data = MANUAL_KEY_PLAYERS.get(player_name, {"attack": 1.03})
        base_attack = player_data.get("attack", 1.03)
        excess = base_attack - 1.0
        weight = weights[i] if i < len(weights) else 0.1
        total_boost += (excess * weight)

    total_boost = max(1.0, min(total_boost, 1.25))
    return round(total_boost, 3)

def get_team_star_impact(team_name):
    return calculate_squad_depth_boost(team_name)
