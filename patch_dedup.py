with open('prediction_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

if content.startswith('\ufeff'):
    content = content[1:]

original_len = len(content.splitlines())
changes = 0

# === FIX 1: Add names_match function after normalize_name ===
if 'def names_match' not in content:
    match_func = '''
def names_match(name1, name2):
    n1 = normalize_name(name1).lower().strip()
    n2 = normalize_name(name2).lower().strip()
    if n1 == n2:
        return True
    for suffix in [' jr', ' junior', ' sr', ' senior', ' ii', ' iii']:
        n1 = n1.replace(suffix, '').strip()
        n2 = n2.replace(suffix, '').strip()
    if n1 == n2:
        return True
    if len(n1) > 3 and len(n2) > 3:
        if n1 in n2 or n2 in n1:
            return True
    return False


'''
    marker = 'def derive_star_players'
    idx = content.find(marker)
    if idx > -1:
        content = content[:idx] + match_func + content[idx:]
        print("  [1] Added names_match() for fuzzy dedup")
        changes += 1

# === FIX 2: Raise min goals and add min gpm in derive ===
old_min = 'player_goals = player_goals[player_goals["total_goals"] >= CONFIG["STAR_MIN_GOALS"]]'
new_min = '''player_goals = player_goals[player_goals["total_goals"] >= CONFIG["STAR_MIN_GOALS"]]
    player_goals = player_goals[player_goals["gpm"] >= 0.20]'''

# But gpm is calculated AFTER this filter... need to restructure slightly
# Actually gpm is calculated after. Let me find the right spot.
# Let me instead add the gpm filter AFTER gpm is calculated
old_gpm_calc = '    player_goals["gpm"] = player_goals["total_goals"] / player_goals["matches"]'
new_gpm_calc = '''    player_goals["gpm"] = player_goals["total_goals"] / player_goals["matches"]
    player_goals = player_goals[player_goals["gpm"] >= 0.20]
    if player_goals.empty:
        return {}'''

if old_gpm_calc in content:
    content = content.replace(old_gpm_calc, new_gpm_calc, 1)
    print("  [2] Added min gpm 0.20 filter (removes defenders)")
    changes += 1

# Also bump STAR_MIN_GOALS from 3 to 4
old_mingoals = '"STAR_MIN_GOALS": 3,'
new_mingoals = '"STAR_MIN_GOALS": 4,'
if old_mingoals in content:
    content = content.replace(old_mingoals, new_mingoals, 1)
    print("  [3] STAR_MIN_GOALS: 3 -> 4")
    changes += 1

# === FIX 3: Update merge logic to use names_match ===
old_merge_derived = '''    for name, data in derived.items():
        norm = normalize_name(name) if name != name else name
        if name not in merged:
            merged[name] = data
        else:
            old_boost = merged[name].get("attack", 1.0)
            new_boost = data.get("attack", 1.0)
            merged[name]["attack"] = round(max(old_boost, new_boost), 3)'''

new_merge_derived = '''    for name, data in derived.items():
        matched_key = None
        for existing_name in merged:
            if names_match(name, existing_name):
                matched_key = existing_name
                break
        if matched_key:
            old_boost = merged[matched_key].get("attack", 1.0)
            new_boost = data.get("attack", 1.0)
            merged[matched_key]["attack"] = round(max(old_boost, new_boost), 3)
        else:
            merged[name] = data'''

if old_merge_derived in content:
    content = content.replace(old_merge_derived, new_merge_derived, 1)
    print("  [4] Merge now uses names_match() for fuzzy dedup")
    changes += 1
else:
    print("  [4] Could not find merge block - checking alt...")
    # Maybe the old merge wasn't patched last time, try original
    alt_old = '''    for name, data in derived.items():
        if name not in merged:
            merged[name] = data
        else:
            old_boost = merged[name].get("attack", 1.0)
            new_boost = data.get("attack", 1.0)
            merged[name]["attack"] = round(max(old_boost, new_boost), 3)'''
    if alt_old in content:
        content = content.replace(alt_old, new_merge_derived, 1)
        print("  [4] Merge now uses names_match() (from original)")
        changes += 1

with open('prediction_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(content.splitlines())
print("")
print("Changes: " + str(changes))
print("Lines: " + str(original_len) + " -> " + str(new_len))
