import re

with open('prediction_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove BOM if present
if content.startswith('\ufeff'):
    content = content[1:]

original_len = len(content.splitlines())
print(f"Original: {original_len} lines")
changes = 0

# === PATCH 1: Add timedelta to import ===
old_import = 'from datetime import datetime'
new_import = 'from datetime import datetime, timedelta'
if 'timedelta' not in content:
    content = content.replace(old_import, new_import, 1)
    print("  [1] Added timedelta to imports")
    changes += 1
else:
    print("  [1] timedelta already imported")

# === PATCH 2: Update CONFIG values ===
config_patches = [
    ('"RANK_WEIGHT_TOP": 0.40', '"RANK_WEIGHT_TOP": 0.30'),
    ('"RANK_WEIGHT_OTHER": 0.25', '"RANK_WEIGHT_OTHER": 0.20'),
    ('"MAX_RATIO": 1.35', '"MAX_RATIO": 1.40'),
    ('"DIXON_COLES_RHO": -0.04', '"DIXON_COLES_RHO": -0.08'),
]
for old, new in config_patches:
    if old in content:
        content = content.replace(old, new)
        key = old.split(':')[0].strip().strip('"')
        print(f"  [2] CONFIG {key}: {old.split(':')[1].strip()} -> {new.split(':')[1].strip()}")
        changes += 1

# === PATCH 3: Add new CONFIG keys ===
if '"H2H_MATCHES"' not in content:
    new_keys = '''    "H2H_MATCHES": 8,
    "H2H_WEIGHT": 0.05,
    "STAR_MIN_GOALS": 3,
    "STAR_RECENT_DAYS": 900,'''
    marker = '    "DEFAULT_TOURNAMENT_WEIGHT": 0.65,'
    if marker in content:
        content = content.replace(marker, marker + '\n' + new_keys)
        print("  [3] Added H2H_MATCHES, H2H_WEIGHT, STAR_MIN_GOALS, STAR_RECENT_DAYS to CONFIG")
        changes += 1
    else:
        print("  [3] WARNING: Could not find DEFAULT_TOURNAMENT_WEIGHT marker")
else:
    print("  [3] New CONFIG keys already present")

# === PATCH 4: Add load_goalscorers after load_rankings ===
if 'def load_goalscorers' not in content:
    gs_func = '''

_goalscorers_cache = None


def load_goalscorers():
    global _goalscorers_cache
    if _goalscorers_cache is not None:
        return _goalscorers_cache
    try:
        df = pd.read_csv("data/goalscorers.csv")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        _goalscorers_cache = df
        return df
    except FileNotFoundError:
        return pd.DataFrame()

'''
    marker = 'def get_all_teams'
    idx = content.find(marker)
    if idx > -1:
        content = content[:idx] + gs_func + content[idx:]
        print("  [4] Added load_goalscorers() before get_all_teams")
        changes += 1
    else:
        print("  [4] WARNING: Could not find get_all_teams marker")
else:
    print("  [4] load_goalscorers already exists")

# === PATCH 5: Add derive_star_players before get_team_star_impact ===
if 'def derive_star_players' not in content:
    derive_func = '''
def derive_star_players(team):
    gs = load_goalscorers()
    if gs.empty:
        return {}
    cutoff = datetime.now() - timedelta(days=CONFIG["STAR_RECENT_DAYS"])
    recent = gs[gs["date"] >= cutoff].copy()
    if recent.empty:
        return {}
    team_goals = recent[recent["team"] == team].copy()
    if "own_goal" in team_goals.columns:
        team_goals = team_goals[team_goals["own_goal"] != True]
    if team_goals.empty:
        return {}
    if "scorer" not in team_goals.columns:
        return {}
    player_goals = team_goals.groupby("scorer").agg(
        total_goals=("scorer", "count"),
        matches=("date", "nunique")
    ).reset_index()
    player_goals = player_goals[player_goals["total_goals"] >= CONFIG["STAR_MIN_GOALS"]]
    if player_goals.empty:
        return {}
    player_goals["gpm"] = player_goals["total_goals"] / player_goals["matches"]
    team_matches = recent[(recent["home_team"] == team) | (recent["away_team"] == team)]
    team_match_count = team_matches["date"].nunique()
    if team_match_count < 1:
        team_match_count = 1
    team_total_goals = len(team_goals)
    team_avg_gpm = team_total_goals / team_match_count if team_match_count > 0 else 1.0
    result = {}
    for _, row in player_goals.iterrows():
        name = row["scorer"]
        gpm = row["gpm"]
        if team_avg_gpm > 0:
            relative = gpm / team_avg_gpm
        else:
            relative = 1.0
        boost = 1.0 + min(0.18, gpm * 0.08 + (relative - 1.0) * 0.04)
        boost = max(1.02, min(boost, 1.20))
        result[name] = {"attack": round(boost, 3), "status": "active", "source": "data"}
    return result


'''
    marker = 'def get_team_star_impact'
    idx = content.find(marker)
    if idx > -1:
        content = content[:idx] + derive_func + content[idx:]
        print("  [5] Added derive_star_players() before get_team_star_impact")
        changes += 1
    else:
        print("  [5] WARNING: Could not find get_team_star_impact marker")
else:
    print("  [5] derive_star_players already exists")

# === PATCH 6: Replace get_team_star_impact to merge manual + derived ===
old_star = '''def get_team_star_impact(team):
    if team not in STAR_PLAYERS:
        return {"attack": 1.0, "players": []}
    players = STAR_PLAYERS[team]
    active = {k: v for k, v in players.items() if v.get("status") == "active"}
    if not active:
        return {"attack": 1.0, "players": []}
    total_boost = 1.0
    for name, data in active.items():
        individual = data.get("attack", 1.0) - 1.0
        total_boost += individual * 0.7
    total_boost = min(total_boost, 1.20)
    return {"attack": total_boost, "players": list(active.keys())}'''

new_star = '''def get_team_star_impact(team):
    manual = STAR_PLAYERS.get(team, {})
    derived = derive_star_players(team)
    merged = {}
    for name, data in manual.items():
        if data.get("status") == "active":
            merged[name] = data.copy()
    for name, data in derived.items():
        if name not in merged:
            merged[name] = data
        else:
            old_boost = merged[name].get("attack", 1.0)
            new_boost = data.get("attack", 1.0)
            merged[name]["attack"] = round(max(old_boost, new_boost), 3)
    if not merged:
        return {"attack": 1.0, "players": []}
    total_boost = 1.0
    for name, data in merged.items():
        individual = data.get("attack", 1.0) - 1.0
        total_boost += individual * 0.7
    total_boost = min(total_boost, 1.20)
    return {"attack": round(total_boost, 3), "players": list(merged.keys())}'''

if old_star in content:
    content = content.replace(old_star, new_star)
    print("  [6] Upgraded get_team_star_impact() to merge manual + derived")
    changes += 1
else:
    print("  [6] get_team_star_impact not matched (may already be upgraded)")

# === PATCH 7: Add get_head_to_head before predict ===
if 'def get_head_to_head' not in content:
    h2h_func = '''
def get_head_to_head(team_a, team_b):
    df = load_results()
    if df.empty:
        return {"factor_a": 1.0, "factor_b": 1.0, "matches": 0, "wins_a": 0, "wins_b": 0, "draws": 0}
    h2h_n = CONFIG["H2H_MATCHES"]
    mask_ab = (df["home_team"] == team_a) & (df["away_team"] == team_b)
    mask_ba = (df["home_team"] == team_b) & (df["away_team"] == team_a)
    matches = df[mask_ab | mask_ba].copy()
    if matches.empty:
        return {"factor_a": 1.0, "factor_b": 1.0, "matches": 0, "wins_a": 0, "wins_b": 0, "draws": 0}
    if "date" in matches.columns:
        matches = matches.sort_values("date")
    matches = matches.tail(h2h_n)
    wins_a = 0
    wins_b = 0
    draws = 0
    goals_a = 0
    goals_b = 0
    for _, r in matches.iterrows():
        if r["home_team"] == team_a:
            ga = r.get("home_score", 0)
            gb = r.get("away_score", 0)
        else:
            ga = r.get("away_score", 0)
            gb = r.get("home_score", 0)
        goals_a += ga
        goals_b += gb
        if ga > gb:
            wins_a += 1
        elif gb > ga:
            wins_b += 1
        else:
            draws += 1
    n = len(matches)
    if n == 0:
        return {"factor_a": 1.0, "factor_b": 1.0, "matches": 0, "wins_a": 0, "wins_b": 0, "draws": 0}
    win_rate_a = wins_a / n
    win_rate_b = wins_b / n
    h2h_w = CONFIG["H2H_WEIGHT"]
    factor_a = 1.0 + h2h_w * (win_rate_a - win_rate_b)
    factor_b = 1.0 + h2h_w * (win_rate_b - win_rate_a)
    return {
        "factor_a": round(factor_a, 4),
        "factor_b": round(factor_b, 4),
        "matches": n,
        "wins_a": wins_a,
        "wins_b": wins_b,
        "draws": draws,
        "goals_a": goals_a,
        "goals_b": goals_b,
    }


'''
    marker = 'def predict('
    idx = content.find(marker)
    if idx > -1:
        content = content[:idx] + h2h_func + content[idx:]
        print("  [7] Added get_head_to_head() before predict")
        changes += 1
    else:
        print("  [7] WARNING: Could not find predict marker")
else:
    print("  [7] get_head_to_head already exists")

# === PATCH 8: Inject h2h into predict() after star boost ===
star_line = '    lambda_b = lambda_b * relative_star_b'
h2h_inject = '''
    # Head-to-head adjustment
    h2h = get_head_to_head(team_a, team_b)
    lambda_a = lambda_a * h2h["factor_a"]
    lambda_b = lambda_b * h2h["factor_b"]
'''
if 'get_head_to_head(team_a, team_b)' not in content.split('def predict')[1] if 'def predict' in content else True:
    if star_line in content:
        content = content.replace(star_line, star_line + '\n' + h2h_inject, 1)
        print("  [8] Injected h2h into predict() after star boost")
        changes += 1
    else:
        print("  [8] WARNING: Could not find star_line marker in predict")
else:
    print("  [8] predict already uses h2h")

# === PATCH 9: Add h2h fields to return dict ===
if '"h2h_matches"' not in content:
    ret_marker = '        "home": home,'
    h2h_fields = '''        "h2h_matches": h2h["matches"],
        "h2h_wins_a": h2h.get("wins_a", 0),
        "h2h_wins_b": h2h.get("wins_b", 0),
        "h2h_draws": h2h.get("draws", 0),'''
    if ret_marker in content:
        content = content.replace(ret_marker, ret_marker + '\n' + h2h_fields, 1)
        print("  [9] Added h2h fields to return dict")
        changes += 1
    else:
        print("  [9] WARNING: Could not find return marker")
else:
    print("  [9] h2h return fields already present")

# === SAVE ===
with open('prediction_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(content.splitlines())
print(f"\nTotal changes: {changes}")
print(f"Lines: {original_len} -> {new_len} (+{new_len - original_len})")
