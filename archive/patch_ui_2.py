with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
if content.startswith('\ufeff'):
    content = content[1:]
changes = 0

# === 5: Add new helper functions before build_match_insight ===
helpers = []
helpers.append("")
helpers.append("")
helpers.append("def get_match_badge(match_type):")
helpers.append("    badges = {")
helpers.append('        "Elite Clash": \'<span class="match-badge badge-elite">' + "\u2694\ufe0f\U0001f525 ELITE CLASH \U0001f525\u2694\ufe0f" + '</span>\',')
helpers.append('        "Total Mismatch": \'<span class="match-badge badge-mismatch">' + "\U0001f480 TOTAL MISMATCH \U0001f480" + '</span>\',')
helpers.append('        "Clear Favorite": \'<span class="match-badge badge-favorite">' + "\U0001f451 CLEAR FAVORITE \U0001f451" + '</span>\',')
helpers.append('        "Competitive Match": \'<span class="match-badge badge-competitive">' + "\u26a1 COMPETITIVE \u26a1" + '</span>\',')
helpers.append("    }")
helpers.append('    return badges.get(match_type, \'<span class="match-badge badge-competitive">' + "\u26bd MATCH \u26bd" + "</span>')")
helpers.append("")
helpers.append("")
helpers.append("def get_venue_badge(neutral):")
helpers.append("    if neutral:")
helpers.append("        return '<span class=" + '"match-badge badge-venue">' + "\U0001f3df\ufe0f NEUTRAL \U0001f3df\ufe0f" + "</span>'")
helpers.append("    return '<span class=" + '"match-badge badge-venue">' + "\U0001f3e0 HOME ADVANTAGE \U0001f3e0" + "</span>'")
helpers.append("")
helpers.append("")
helpers.append("def build_stars_html(players, boost):")
helpers.append("    if not players:")
helpers.append("        return '<div style=" + '"color:#666688;font-style:italic;"' + ">No star data</div>'")
helpers.append("    h = '<div style=" + '"margin-bottom:6px;color:#ffd700;font-weight:700;"' + ">" + "\u2b50 Boost: x' + str(boost) + '</div>'")
helpers.append("    for p in players[:5]:")
helpers.append("        h += '<span class=" + '"star-player">' + "\U0001f31f ' + str(p) + '</span>'")
helpers.append("    return h")
helpers.append("")
helpers.append("")
helpers.append("def build_h2h_html(result, team_a, team_b):")
helpers.append('    matches = result.get("h2h_matches", 0)')
helpers.append("    if matches == 0:")
helpers.append("        return '<div style=" + '"color:#666688;font-style:italic;"' + ">" + "\U0001f937 No previous meetings found</div>'")
helpers.append('    wa = result.get("h2h_wins_a", 0)')
helpers.append('    wb = result.get("h2h_wins_b", 0)')
helpers.append('    d = result.get("h2h_draws", 0)')
helpers.append("    total = wa + wb + d")
helpers.append("    if total == 0:")
helpers.append("        total = 1")
helpers.append("    pct_a = round(100 * wa / total)")
helpers.append("    pct_d = round(100 * d / total)")
helpers.append("    pct_b = 100 - pct_a - pct_d")

# This approach is getting way too messy with all the quoting layers.
# Let me write the helpers file directly instead.

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Part 2 abandoned - quoting too complex for inline approach")
