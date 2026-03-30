import unicodedata

with open('prediction_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

if content.startswith('\ufeff'):
    content = content[1:]

original_len = len(content.splitlines())
changes = 0

# === FIX 1: Add accent normalization helper before derive_star_players ===
if 'def normalize_name' not in content:
    norm_func = '''
def normalize_name(name):
    if not isinstance(name, str):
        return str(name)
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = nfkd.encode("ascii", "ignore").decode("ascii")
    return ascii_name.strip()


'''
    marker = 'def derive_star_players'
    idx = content.find(marker)
    if idx > -1:
        content = content[:idx] + norm_func + content[idx:]
        print("  [1] Added normalize_name() helper")
        changes += 1

# === FIX 2: Add unicodedata import ===
if 'import unicodedata' not in content:
    content = content.replace('import math', 'import math\nimport unicodedata', 1)
    print("  [2] Added unicodedata import")
    changes += 1

# === FIX 3: Update derive_star_players to normalize names ===
old_derive_line = '        result[name] = {"attack": round(boost, 3), "status": "active", "source": "data"}'
new_derive_line = '        norm = normalize_name(name)\n        result[norm] = {"attack": round(boost, 3), "status": "active", "source": "data"}'
if old_derive_line in content:
    content = content.replace(old_derive_line, new_derive_line, 1)
    print("  [3] derive_star_players now normalizes scorer names")
    changes += 1

# === FIX 4: Normalize manual names during merge in get_team_star_impact ===
old_merge = '''    for name, data in manual.items():
        if data.get("status") == "active":
            merged[name] = data.copy()
    for name, data in derived.items():
        if name not in merged:
            merged[name] = data
        else:
            old_boost = merged[name].get("attack", 1.0)
            new_boost = data.get("attack", 1.0)
            merged[name]["attack"] = round(max(old_boost, new_boost), 3)'''

new_merge = '''    for name, data in manual.items():
        if data.get("status") == "active":
            norm = normalize_name(name)
            merged[norm] = data.copy()
    for name, data in derived.items():
        norm = normalize_name(name) if name != name else name
        if name not in merged:
            merged[name] = data
        else:
            old_boost = merged[name].get("attack", 1.0)
            new_boost = data.get("attack", 1.0)
            merged[name]["attack"] = round(max(old_boost, new_boost), 3)'''

if old_merge in content:
    content = content.replace(old_merge, new_merge, 1)
    print("  [4] get_team_star_impact now normalizes manual names for matching")
    changes += 1

# === FIX 5: Raise star cap and reduce per-player contribution for balance ===
# Change cap from 1.20 to 1.25, and reduce per-player from 0.7 to 0.5
# This means: more players needed to hit cap, more differentiation
old_boost_calc = '''    total_boost = 1.0
    for name, data in merged.items():
        individual = data.get("attack", 1.0) - 1.0
        total_boost += individual * 0.7
    total_boost = min(total_boost, 1.20)'''

new_boost_calc = '''    sorted_players = sorted(merged.values(), key=lambda x: x.get("attack", 1.0), reverse=True)
    total_boost = 1.0
    for i, data in enumerate(sorted_players):
        individual = data.get("attack", 1.0) - 1.0
        diminish = 0.55 / (1.0 + 0.3 * i)
        total_boost += individual * diminish
    total_boost = min(total_boost, 1.25)'''

if old_boost_calc in content:
    content = content.replace(old_boost_calc, new_boost_calc, 1)
    print("  [5] Star boost: diminishing returns per player, cap raised to 1.25")
    changes += 1

with open('prediction_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(content.splitlines())
print("")
print("Changes: " + str(changes))
print("Lines: " + str(original_len) + " -> " + str(new_len))
