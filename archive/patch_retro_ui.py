with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

if content.startswith('\ufeff'):
    content = content[1:]

original_len = len(content.splitlines())
changes = 0

# ============================================
# PATCH 1: Replace CSS block with retro theme
# ============================================
old_css_start = content.find("<style>")
old_css_end = content.find("</style>") + len("</style>")

retro_css = """<style>
@keyframes pulse { 0%,100%{transform:scale(1);} 50%{transform:scale(1.05);} }
@keyframes marquee { 0%{transform:translateX(100%);} 100%{transform:translateX(-100%);} }
html, body, [class*="css"] { font-family:"Impact","Arial Black","Trebuchet MS",sans-serif; }
.main { background:linear-gradient(180deg,#0a0a2e 0%,#1a0a3e 50%,#0a1a2e 100%); color:#e0e0ff; }
.block-container { padding-top:1rem; padding-bottom:2rem; max-width:1200px; }
.hero-retro { background:linear-gradient(135deg,#000428 0%,#004e92 50%,#000428 100%); border:3px solid #00f0ff; border-radius:20px; padding:30px; margin-bottom:1.5rem; text-align:center; box-shadow:0 0 30px rgba(0,240,255,0.3),inset 0 0 30px rgba(0,240,255,0.1); overflow:hidden; }
.hero-title-retro { font-size:3rem; font-weight:900; color:#ffd700; text-shadow:3px 3px 0px #ff6600,0 0 20px rgba(255,215,0,0.5); letter-spacing:2px; }
.hero-sub-retro { font-size:1.1rem; color:#00f0ff; text-shadow:0 0 10px #00f0ff; letter-spacing:3px; text-transform:uppercase; }
.hero-marquee { margin-top:12px; overflow:hidden; white-space:nowrap; }
.hero-marquee span { display:inline-block; animation:marquee 15s linear infinite; font-size:0.9rem; color:#ff00aa; }
.retro-card { background:linear-gradient(180deg,#141430 0%,#1a1a40 100%); border:2px solid #00f0ff; border-radius:16px; padding:22px; margin-bottom:1rem; box-shadow:0 0 15px rgba(0,240,255,0.15); }
.retro-card-title { font-size:1.2rem; font-weight:900; color:#ffd700; text-shadow:1px 1px 0 #ff6600; margin-bottom:12px; letter-spacing:1px; text-transform:uppercase; }
.retro-card-pink { border-color:#ff00aa; box-shadow:0 0 15px rgba(255,0,170,0.15); }
.retro-card-green { border-color:#00ff88; box-shadow:0 0 15px rgba(0,255,136,0.15); }
.retro-card-gold { border-color:#ffd700; box-shadow:0 0 15px rgba(255,215,0,0.15); }
.vs-retro { display:flex; align-items:center; justify-content:space-between; padding:10px 0; }
.team-retro { font-size:1.5rem; font-weight:900; color:#00f0ff; text-shadow:0 0 10px rgba(0,240,255,0.5); }
.team-rank-retro { color:#8888aa; font-size:0.85rem; font-family:"Courier New",monospace; }
.vs-badge { font-size:1.4rem; font-weight:900; color:#ffd700; text-shadow:2px 2px 0 #ff6600; padding:8px 16px; border:2px solid #ffd700; border-radius:50%%; background:rgba(255,215,0,0.1); animation:pulse 2s ease-in-out infinite; }
.match-badge { display:inline-block; padding:8px 16px; border-radius:20px; font-size:0.9rem; font-weight:900; margin:6px 8px 6px 0; letter-spacing:1px; text-transform:uppercase; }
.badge-elite { background:linear-gradient(90deg,#ff6600,#ff0033); color:white; border:2px solid #ff0033; animation:pulse 2s ease-in-out infinite; }
.badge-mismatch { background:linear-gradient(90deg,#8b0000,#4a0000); color:#ff6666; border:2px solid #ff3333; }
.badge-favorite { background:linear-gradient(90deg,#004e92,#0066cc); color:#88ccff; border:2px solid #00aaff; }
.badge-competitive { background:linear-gradient(90deg,#006644,#00aa66); color:#88ffcc; border:2px solid #00ff88; }
.badge-venue { background:rgba(255,215,0,0.15); color:#ffd700; border:2px solid #ffd700; }
.metric-retro { display:flex; gap:16px; flex-wrap:wrap; margin:12px 0; }
.metric-box-retro { flex:1; min-width:140px; background:linear-gradient(180deg,#1a1a40 0%,#0a0a2e 100%); border:2px solid #00f0ff; border-radius:14px; padding:16px; text-align:center; }
.metric-label-retro { font-size:0.8rem; color:#8888cc; text-transform:uppercase; letter-spacing:2px; margin-bottom:6px; }
.metric-value-retro { font-size:2.2rem; font-weight:900; color:#00f0ff; text-shadow:0 0 15px rgba(0,240,255,0.5); }
.metric-value-gold { color:#ffd700; text-shadow:0 0 15px rgba(255,215,0,0.5); }
.metric-value-pink { color:#ff00aa; text-shadow:0 0 15px rgba(255,0,170,0.5); }
.prob-label-retro { display:flex; justify-content:space-between; font-size:0.9rem; color:#ccccff; margin-bottom:4px; font-weight:700; }
.prob-track-retro { width:100%%; height:18px; background:#0a0a2e; border-radius:10px; border:1px solid #333366; overflow:hidden; margin-bottom:10px; }
.prob-fill-cyan { height:100%%; background:linear-gradient(90deg,#004466,#00f0ff); border-radius:10px; box-shadow:0 0 10px rgba(0,240,255,0.4); }
.prob-fill-gold2 { height:100%%; background:linear-gradient(90deg,#665500,#ffd700); border-radius:10px; box-shadow:0 0 10px rgba(255,215,0,0.4); }
.prob-fill-pink { height:100%%; background:linear-gradient(90deg,#660044,#ff00aa); border-radius:10px; box-shadow:0 0 10px rgba(255,0,170,0.4); }
.score-pill-retro { display:inline-block; padding:10px 16px; margin:5px; border-radius:12px; background:linear-gradient(180deg,#1a1a40,#0a0a2e); border:2px solid #00f0ff; font-weight:900; font-size:1.1rem; color:#00f0ff; text-shadow:0 0 8px rgba(0,240,255,0.4); }
.score-pill-top { border-color:#ffd700; color:#ffd700; text-shadow:0 0 8px rgba(255,215,0,0.4); font-size:1.3rem; animation:pulse 2s ease-in-out infinite; }
.star-player { display:inline-block; padding:6px 12px; margin:4px; border-radius:10px; background:linear-gradient(90deg,#1a1a40,#2a1a50); border:1px solid #ffd700; color:#ffd700; font-size:0.85rem; font-weight:700; }
.h2h-bar { display:flex; height:30px; border-radius:8px; overflow:hidden; margin:10px 0; border:1px solid #333366; }
.h2h-win { background:#00f0ff; }
.h2h-draw { background:#ffd700; }
.h2h-loss { background:#ff00aa; }
.insight-retro { border-left:4px solid #ffd700; background:linear-gradient(90deg,rgba(255,215,0,0.05),transparent); padding:14px 18px; border-radius:0 12px 12px 0; color:#ccccff; line-height:1.6; font-family:"Trebuchet MS",sans-serif; }
.retro-divider { border:none; height:2px; background:linear-gradient(90deg,transparent,#00f0ff,#ffd700,#ff00aa,transparent); margin:1.2rem 0; }
.stButton > button { width:100%%; background:linear-gradient(135deg,#ff6600 0%%,#ff0033 100%%); color:white; border:2px solid #ffd700; border-radius:14px; padding:0.8rem 1rem; font-weight:900; font-size:1rem; letter-spacing:1px; text-transform:uppercase; box-shadow:0 0 20px rgba(255,102,0,0.3); }
.stButton > button:hover { background:linear-gradient(135deg,#ff0033 0%%,#cc0066 100%%); color:white; border-color:#00f0ff; }
.stSelectbox label { color:#00f0ff !important; font-weight:700; text-transform:uppercase; letter-spacing:1px; }
.stCheckbox label { color:#ffd700 !important; font-weight:700; }
.stTabs [data-baseweb="tab-list"] { gap:4px; }
.stTabs [data-baseweb="tab"] { border-radius:12px 12px 0 0; padding:10px 16px; font-weight:700; color:#8888cc; background:#141430; border:1px solid #333366; }
.stTabs [aria-selected="true"] { background:#00f0ff !important; color:#0a0a2e !important; border-color:#00f0ff !important; }
</style>"""

if old_css_start > -1 and old_css_end > old_css_start:
    content = content[:old_css_start] + retro_css + content[old_css_end:]
    print("  [1] Replaced CSS with retro theme")
    changes += 1

# ============================================
# PATCH 2: Replace hero section
# ============================================
old_hero = '''<div class="hero">
    <div class="hero-title">Mundialista AI</div>
    <div class="hero-subtitle">International Match Intelligence</div>
    <div class="hero-tag">Refined match predictions - Global national teams - Visual-first analytics</div>
</div>'''

new_hero = '''<div class="hero-retro">
    <div class="hero-title-retro">\u26bd MUNDIALISTA AI \U0001f3c6</div>
    <div class="hero-sub-retro">\U0001f30d International Match Intelligence \U0001f30d</div>
    <div class="hero-marquee"><span>\u26bd\U0001f525 Dixon-Coles v6.1 + Auto Stars + H2H + 47K Goals \U0001f525\u26bd \U0001f3df\ufe0f 45,000+ Matches \U0001f3df\ufe0f \U0001f31f 200+ Nations \U0001f31f</span></div>
</div>'''

if old_hero in content:
    content = content.replace(old_hero, new_hero)
    print("  [2] Replaced hero with retro hero")
    changes += 1

# ============================================
# PATCH 3: Replace card classes
# ============================================
content = content.replace('class="card"', 'class="retro-card"')
content = content.replace('class="card-title"', 'class="retro-card-title"')
content = content.replace('"card ', '"retro-card ')
print("  [3] Replaced card classes")
changes += 1

# ============================================
# PATCH 4: Replace badge_html with get_match_badge
# ============================================
old_badge_func = '''def badge_html(text, kind="green"):
    klass = {"green": "badge badge-green", "gold": "badge badge-gold", "gray": "badge badge-gray"}.get(kind, "badge badge-green")
    return '<span class="' + klass + '">' + text + '</span>\'''''

# Add new helper functions before get_team_list or after badge_html
new_helpers = '''
def get_match_badge(match_type):
    badges = {
        "Elite Clash": '<span class="match-badge badge-elite">\u2694\ufe0f\U0001f525 ELITE CLASH \U0001f525\u2694\ufe0f</span>',
        "Total Mismatch": '<span class="match-badge badge-mismatch">\U0001f480 TOTAL MISMATCH \U0001f480</span>',
        "Clear Favorite": '<span class="match-badge badge-favorite">\U0001f451 CLEAR FAVORITE \U0001f451</span>',
        "Competitive Match": '<span class="match-badge badge-competitive">\u26a1 COMPETITIVE \u26a1</span>',
    }
    return badges.get(match_type, '<span class="match-badge badge-competitive">\u26bd MATCH \u26bd</span>')


def get_venue_badge(neutral):
    if neutral:
        return '<span class="match-badge badge-venue">\U0001f3df\ufe0f NEUTRAL \U0001f3df\ufe0f</span>'
    return '<span class="match-badge badge-venue">\U0001f3e0 HOME ADVANTAGE \U0001f3e0</span>'


def build_stars_html(players, boost):
    if not players:
        return '<div style="color:#666688;font-style:italic;">No star data</div>'
    h = '<div style="margin-bottom:6px;color:#ffd700;font-weight:700;">\u2b50 Boost: x' + str(boost) + '</div>'
    for p in players[:5]:
        h += '<span class="star-player">\U0001f31f ' + str(p) + '</span>'
    return h


def build_h2h_html(result, team_a, team_b):
    matches = result.get("h2h_matches", 0)
    if matches == 0:
        return '<div style="color:#666688;font-style:italic;">\U0001f937 No previous meetings found</div>'
    wa = result.get("h2h_wins_a", 0)
    wb = result.get("h2h_wins_b", 0)
    d = result.get("h2h_draws", 0)
    total = wa + wb + d
    if total == 0:
        total = 1
    pct_a = round(100 * wa / total)
    pct_d = round(100 * d / total)
    pct_b = 100 - pct_a - pct_d
    h = '<div style="color:#8888cc;margin-bottom:8px;">\U0001f4ca Last <b>' + str(matches) + '</b> meetings</div>'
    h += '<div class="h2h-bar">'
    if pct_a > 0:
        h += '<div class="h2h-win" style="width:' + str(pct_a) + '%%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">' + str(wa) + 'W</div>'
    if pct_d > 0:
        h += '<div class="h2h-draw" style="width:' + str(pct_d) + '%%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">' + str(d) + 'D</div>'
    if pct_b > 0:
        h += '<div class="h2h-loss" style="width:' + str(pct_b) + '%%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">' + str(wb) + 'W</div>'
    h += '</div>'
    h += '<div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-top:4px;">'
    h += '<span style="color:#00f0ff;">\U0001f3c6 ' + team_a + '</span>'
    h += '<span style="color:#ffd700;">\U0001f91d Draw</span>'
    h += '<span style="color:#ff00aa;">\U0001f3c6 ' + team_b + '</span></div>'
    return h

'''

# Insert new helpers before build_match_insight
marker = 'def build_match_insight'
idx = content.find(marker)
if idx > -1:
    content = content[:idx] + new_helpers + content[idx:]
    print("  [4] Added helper functions")
    changes += 1

# ============================================
# PATCH 5: Update build_match_insight with emojis
# ============================================
old_insight_start = '    if abs(a - b) <= 6:'
old_edge1 = '        edge = team_a + " and " + team_b + " project as closely matched."'
new_edge1 = '        edge = "\U0001f91c\U0001f91b " + team_a + " and " + team_b + " are neck and neck!"'
if old_edge1 in content:
    content = content.replace(old_edge1, new_edge1)

old_edge2 = '        edge = team_a + " enter as the more likely winner."'
new_edge2 = '        edge = "\U0001f4aa " + team_a + " have the edge in this matchup."'
if old_edge2 in content:
    content = content.replace(old_edge2, new_edge2)

old_edge3 = '        edge = team_b + " look slightly stronger in the current model."'
new_edge3 = '        edge = "\U0001f4aa " + team_b + " look stronger going into this one."'
if old_edge3 in content:
    content = content.replace(old_edge3, new_edge3)

old_dr1 = '        dr = "Draw probability is elevated, pointing to a compact match."'
new_dr1 = '        dr = "\U0001f91d High draw probability - expect a tense, tight match!"'
if old_dr1 in content:
    content = content.replace(old_dr1, new_dr1)

old_dr2 = '        dr = "Draw probability is modest, suggesting a decisive result."'
new_dr2 = '        dr = "\u26a1 Low draw chance - someone is winning this!"'
if old_dr2 in content:
    content = content.replace(old_dr2, new_dr2)

old_dr3 = '        dr = "A draw remains a meaningful live outcome."'
new_dr3 = '        dr = "\U0001f3b2 A draw is still very much on the cards."'
if old_dr3 in content:
    content = content.replace(old_dr3, new_dr3)

old_gl1 = '        gl = "Expected goals indicate a potentially open game."'
new_gl1 = '        gl = "\U0001f525 Goals expected! This could be a thriller!"'
if old_gl1 in content:
    content = content.replace(old_gl1, new_gl1)

old_gl2 = '        gl = "Expected goals suggest a lower-scoring contest."'
new_gl2 = '        gl = "\U0001f512 Tight game expected. Every goal will matter."'
if old_gl2 in content:
    content = content.replace(old_gl2, new_gl2)

old_gl3 = '        gl = "Expected goals point to a moderate scoring environment."'
new_gl3 = '        gl = "\u26bd Balanced scoring - 2-3 goals likely."'
if old_gl3 in content:
    content = content.replace(old_gl3, new_gl3)

print("  [5] Updated match insight with emojis")
changes += 1

# ============================================
# PATCH 6: Replace match setup section
# ============================================
old_setup = """st.markdown('<div class="card"><div class="card-title">Match Setup</div>', unsafe_allow_html=True)"""
new_setup = """st.markdown('<div class="retro-card"><div class="retro-card-title">\U0001f3ae Match Setup \U0001f3ae</div>', unsafe_allow_html=True)"""
# This was already handled by class replacement, but let's add emojis
old_matchsetup = 'Match Setup</div>'
new_matchsetup = '\U0001f3ae Match Setup \U0001f3ae</div>'
content = content.replace(old_matchsetup, new_matchsetup, 1)
print("  [6] Added emojis to match setup")
changes += 1

# ============================================
# PATCH 7: Replace VS line with retro style
# ============================================
old_vs = """    v = '<div class="vs-line"><div><div class="team-name">' + da + '</div>'
    v += '<div class="team-rank">FIFA Rank: ' + str(rk_a) + '</div></div>'
    v += '<div class="vs-center">VS</div>'
    v += '<div style="text-align:right;"><div class="team-name">' + db + '</div>'
    v += '<div class="team-rank">FIFA Rank: ' + str(rk_b) + '</div></div></div>'"""

new_vs = """    v = '<div class="vs-retro"><div><div class="team-retro">\u26bd ' + da + '</div>'
    v += '<div class="team-rank-retro">\U0001f4ca FIFA #' + str(rk_a) + '</div></div>'
    v += '<div class="vs-badge">\u26a1VS\u26a1</div>'
    v += '<div style="text-align:right;"><div class="team-retro">' + db + ' \u26bd</div>'
    v += '<div class="team-rank-retro">\U0001f4ca FIFA #' + str(rk_b) + '</div></div></div>'"""

if old_vs in content:
    content = content.replace(old_vs, new_vs)
    print("  [7] Replaced VS line with retro")
    changes += 1

# ============================================
# PATCH 8: Replace badge line
# ============================================
old_badge_line = "    st.markdown(badge_html(mt, \"gold\") + badge_html(vl, \"green\"), unsafe_allow_html=True)"
new_badge_line = "    st.markdown(get_match_badge(mt) + get_venue_badge(neutral), unsafe_allow_html=True)"
if old_badge_line in content:
    content = content.replace(old_badge_line, new_badge_line)
    print("  [8] Replaced badges with retro match badges")
    changes += 1

# ============================================
# PATCH 9: Replace metric boxes
# ============================================
old_metrics = """    m = '<div class="metric-row">'
    m += '<div class="metric-box"><div class="metric-label">' + da + ' Win</div>'
    m += '<div class="metric-value">' + wa + '%</div>'
    m += '<div class="metric-sub">Model win probability</div></div>'
    m += '<div class="metric-box"><div class="metric-label">Draw</div>'
    m += '<div class="metric-value" style="color:#8A6B00;">' + dv + '%</div>'
    m += '<div class="metric-sub">Shared outcome probability</div></div>'
    m += '<div class="metric-box"><div class="metric-label">' + db + ' Win</div>'
    m += '<div class="metric-value">' + wb + '%</div>'
    m += '<div class="metric-sub">Model win probability</div></div></div>'"""

new_metrics = """    m = '<div class="metric-retro">'
    m += '<div class="metric-box-retro"><div class="metric-label-retro">\U0001f3c6 ' + da + '</div>'
    m += '<div class="metric-value-retro">' + wa + '%%</div></div>'
    m += '<div class="metric-box-retro"><div class="metric-label-retro">\U0001f91d Draw</div>'
    m += '<div class="metric-value-retro metric-value-gold">' + dv + '%%</div></div>'
    m += '<div class="metric-box-retro"><div class="metric-label-retro">\U0001f3c6 ' + db + '</div>'
    m += '<div class="metric-value-retro metric-value-pink">' + wb + '%%</div></div></div>'"""

if old_metrics in content:
    content = content.replace(old_metrics, new_metrics)
    print("  [9] Replaced metrics with retro style")
    changes += 1

# ============================================
# PATCH 10: Replace probability bars
# ============================================
old_prob = """    p = '<div class="prob-wrap">'
    p += '<div class="prob-label-row"><span>' + da + ' win</span><span>' + wa + '%</span></div>'
    p += '<div class="prob-track"><div class="prob-fill-green" style="width:' + wa + '%;"></div></div>'
    p += '<div class="prob-label-row"><span>Draw</span><span>' + dv + '%</span></div>'
    p += '<div class="prob-track"><div class="prob-fill-gold" style="width:' + dv + '%;"></div></div>'
    p += '<div class="prob-label-row"><span>' + db + ' win</span><span>' + wb + '%</span></div>'
    p += '<div class="prob-track"><div class="prob-fill-gray" style="width:' + wb + '%;"></div></div></div>'"""

new_prob = """    p = '<div class="prob-label-retro"><span>\U0001f3c6 ' + da + '</span><span>' + wa + '%%</span></div>'
    p += '<div class="prob-track-retro"><div class="prob-fill-cyan" style="width:' + wa + '%%;"></div></div>'
    p += '<div class="prob-label-retro"><span>\U0001f91d Draw</span><span>' + dv + '%%</span></div>'
    p += '<div class="prob-track-retro"><div class="prob-fill-gold2" style="width:' + dv + '%%;"></div></div>'
    p += '<div class="prob-label-retro"><span>\U0001f3c6 ' + db + '</span><span>' + wb + '%%</span></div>'
    p += '<div class="prob-track-retro"><div class="prob-fill-pink" style="width:' + wb + '%%;"></div></div>'"""

if old_prob in content:
    content = content.replace(old_prob, new_prob)
    print("  [10] Replaced probability bars with retro")
    changes += 1

# ============================================
# PATCH 11: Replace score pills
# ============================================
old_pill = """                    sh += '<span class="score-pill">' + str(sc[0]) + ' - ' + str(sc[1]) + '</span>'"""
new_pill = """                    css_c = "score-pill-top" if idx_s == 0 else "score-pill-retro"
                    pre = "\U0001f451 " if idx_s == 0 else ""
                    sh += '<span class="' + css_c + '">' + pre + str(sc[0]) + '</span>'"""
# Also need to change the for loop to include enumerate
old_for_scores = "            for sc in ts:"
new_for_scores = "            for idx_s, sc in enumerate(ts):"
if old_for_scores in content:
    content = content.replace(old_for_scores, new_for_scores, 1)
if old_pill in content:
    content = content.replace(old_pill, new_pill)
    print("  [11] Replaced score pills with retro + crown for top")
    changes += 1

# ============================================
# PATCH 12: Replace hr with retro divider
# ============================================
content = content.replace('st.markdown("<hr>", unsafe_allow_html=True)', 'st.markdown(\'<div class="retro-divider"></div>\', unsafe_allow_html=True)')
print("  [12] Replaced hr with retro dividers")
changes += 1

# ============================================
# PATCH 13: Replace insight display
# ============================================
old_insight_display = "    st.markdown('<div class=\"insight\">' + ins + '</div>', unsafe_allow_html=True)"
new_insight_display = "    st.markdown('<div class=\"insight-retro\">' + ins + '</div>', unsafe_allow_html=True)"
if old_insight_display in content:
    content = content.replace(old_insight_display, new_insight_display)
    print("  [13] Replaced insight with retro style")
    changes += 1

# ============================================
# PATCH 14: Add star players + H2H sections after probability bars
# ============================================
# Find the expected goals section and add stars + h2h before it
xg_marker = "        st.markdown('<div class=\"retro-card-title\">Expected Goals</div>', unsafe_allow_html=True)"
if xg_marker not in content:
    xg_marker = "        st.markdown('<div class=\"card-title\">Expected Goals</div>', unsafe_allow_html=True)"

# Find the section with s1, s2 = st.columns
cols_marker = '    s1, s2 = st.columns([1, 1])'
if cols_marker in content:
    stars_h2h_section = '''
    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown('<div class="retro-card retro-card-gold"><div class="retro-card-title">\U0001f31f ' + da + ' Stars \U0001f31f</div>', unsafe_allow_html=True)
        st.markdown(build_stars_html(result.get("team_a_stars", []), result.get("team_a_star_boost", 1.0)), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with sc2:
        st.markdown('<div class="retro-card retro-card-gold"><div class="retro-card-title">\U0001f31f ' + db + ' Stars \U0001f31f</div>', unsafe_allow_html=True)
        st.markdown(build_stars_html(result.get("team_b_stars", []), result.get("team_b_star_boost", 1.0)), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="retro-card retro-card-pink"><div class="retro-card-title">\u2694\ufe0f Head-to-Head \u2694\ufe0f</div>', unsafe_allow_html=True)
    st.markdown(build_h2h_html(result, da, db), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

'''
    content = content.replace(cols_marker, stars_h2h_section + cols_marker)
    print("  [14] Added star players + H2H sections")
    changes += 1

# ============================================
# PATCH 15: Add emojis to section titles
# ============================================
content = content.replace("Expected Goals</div>", "\u26bd Expected Goals \u26bd</div>")
content = content.replace("Most Likely Scorelines</div>", "\U0001f3af Top Scores \U0001f3af</div>")
content = content.replace("Model Insight</div>", "\U0001f9e0 AI Match Insight \U0001f9e0</div>")
content = content.replace("Visual Analytics</div>", "\U0001f4c8 Visual Analytics \U0001f4c8</div>")
content = content.replace("Win / Draw / Loss Profile</div>", "\U0001f4ca Win Probability \U0001f4ca</div>")
content = content.replace("How to use</div>", "\U0001f3ae How To Play \U0001f3ae</div>")
print("  [15] Added emojis to section titles")
changes += 1

# ============================================
# PATCH 16: Update expected goals boxes
# ============================================
old_xg = """        x = '<div class="metric-row">'
        x += '<div class="metric-box"><div class="metric-label">' + da + '</div>'
        x += '<div class="metric-value">' + la_s + '</div>'
        x += '<div class="metric-sub">Expected goals</div></div>'
        x += '<div class="metric-box"><div class="metric-label">' + db + '</div>'
        x += '<div class="metric-value">' + lb_s + '</div>'
        x += '<div class="metric-sub">Expected goals</div></div></div>'"""

new_xg = """        x = '<div class="metric-retro">'
        x += '<div class="metric-box-retro"><div class="metric-label-retro">' + da + '</div>'
        x += '<div class="metric-value-retro">' + la_s + '</div></div>'
        x += '<div class="metric-box-retro"><div class="metric-label-retro">' + db + '</div>'
        x += '<div class="metric-value-retro metric-value-pink">' + lb_s + '</div></div></div>'"""

if old_xg in content:
    content = content.replace(old_xg, new_xg)
    print("  [16] Updated expected goals boxes")
    changes += 1

# ============================================
# PATCH 17: Update how-to-use section
# ============================================
old_howto = """        <div class="muted">
            Select two national teams, choose whether the match is on neutral ground, and click
            <strong>Generate Prediction</strong> to view win probabilities, expected goals, likely scorelines,
            model-generated match insight, and full visual analytics charts.
        </div>"""

new_howto = """        <div style="color:#8888cc;line-height:1.8;font-family:Trebuchet MS,sans-serif;">
            1\ufe0f\u20e3 Pick <b style="color:#00f0ff;">Team A</b> (home side)<br>
            2\ufe0f\u20e3 Pick <b style="color:#ff00aa;">Team B</b> (away side)<br>
            3\ufe0f\u20e3 Choose \U0001f3df\ufe0f neutral or \U0001f3e0 home advantage<br>
            4\ufe0f\u20e3 Hit <b style="color:#ffd700;">\u26a1 PREDICT \u26a1</b><br>
            5\ufe0f\u20e3 Win probs, goals, stars, head-to-head, scorelines and more! \U0001f525<br><br>
            <span style="color:#ff00aa;">\U0001f4be Database:</span> 45,000+ matches | 47,000+ goals | 200+ nations<br>
            <span style="color:#00f0ff;">\U0001f9e0 Engine:</span> Dixon-Coles v6.1 + auto stars + H2H<br>
            <span style="color:#ffd700;">\u26a1 Speed:</span> 10,200 Monte Carlo simulations per prediction
        </div>"""

if old_howto in content:
    content = content.replace(old_howto, new_howto)
    print("  [17] Updated how-to section with retro style")
    changes += 1

# ============================================
# SAVE
# ============================================
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(content.splitlines())
print("")
print("Total changes: " + str(changes))
print("Lines: " + str(original_len) + " -> " + str(new_len))
