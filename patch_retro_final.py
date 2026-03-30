# ALL-IN-ONE: Creates CSS, helpers, and patches app.py
# No external files needed

with open('app_v6_backup.py', 'r', encoding='utf-8') as f:
    content = f.read()
if content.startswith('\ufeff'):
    content = content[1:]
original = len(content.splitlines())
changes = 0

# ==================== CSS ====================
css = "<style>\n"
css += "@keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.05);}}\n"
css += "@keyframes marquee{0%{transform:translateX(100%);}100%{transform:translateX(-100%);}}\n"
css += 'html,body,[class*="css"]{font-family:Impact,Arial Black,Trebuchet MS,sans-serif;}\n'
css += ".main{background:linear-gradient(180deg,#0a0a2e,#1a0a3e,#0a1a2e);color:#e0e0ff;}\n"
css += ".block-container{padding-top:1rem;padding-bottom:2rem;max-width:1200px;}\n"
css += ".retro-card{background:linear-gradient(180deg,#141430,#1a1a40);border:2px solid #00f0ff;border-radius:16px;padding:22px;margin-bottom:1rem;box-shadow:0 0 15px rgba(0,240,255,0.15);}\n"
css += ".retro-card-title{font-size:1.2rem;font-weight:900;color:#ffd700;text-shadow:1px 1px 0 #ff6600;margin-bottom:12px;letter-spacing:1px;text-transform:uppercase;}\n"
css += ".retro-card-pink{border-color:#ff00aa;box-shadow:0 0 15px rgba(255,0,170,0.15);}\n"
css += ".retro-card-green{border-color:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.15);}\n"
css += ".retro-card-gold{border-color:#ffd700;box-shadow:0 0 15px rgba(255,215,0,0.15);}\n"
css += ".vs-retro{display:flex;align-items:center;justify-content:space-between;padding:10px 0;}\n"
css += ".team-retro{font-size:1.5rem;font-weight:900;color:#00f0ff;text-shadow:0 0 10px rgba(0,240,255,0.5);}\n"
css += '.team-rank-retro{color:#8888aa;font-size:0.85rem;font-family:"Courier New",monospace;}\n'
css += ".vs-badge{font-size:1.4rem;font-weight:900;color:#ffd700;text-shadow:2px 2px 0 #ff6600;padding:8px 16px;border:2px solid #ffd700;border-radius:50%;background:rgba(255,215,0,0.1);animation:pulse 2s ease-in-out infinite;}\n"
css += ".match-badge{display:inline-block;padding:8px 16px;border-radius:20px;font-size:0.9rem;font-weight:900;margin:6px 8px 6px 0;letter-spacing:1px;text-transform:uppercase;}\n"
css += ".badge-elite{background:linear-gradient(90deg,#ff6600,#ff0033);color:white;border:2px solid #ff0033;animation:pulse 2s ease-in-out infinite;}\n"
css += ".badge-mismatch{background:linear-gradient(90deg,#8b0000,#4a0000);color:#ff6666;border:2px solid #ff3333;}\n"
css += ".badge-favorite{background:linear-gradient(90deg,#004e92,#0066cc);color:#88ccff;border:2px solid #00aaff;}\n"
css += ".badge-competitive{background:linear-gradient(90deg,#006644,#00aa66);color:#88ffcc;border:2px solid #00ff88;}\n"
css += ".badge-venue{background:rgba(255,215,0,0.15);color:#ffd700;border:2px solid #ffd700;}\n"
css += ".metric-retro{display:flex;gap:16px;flex-wrap:wrap;margin:12px 0;}\n"
css += ".metric-box-retro{flex:1;min-width:140px;background:linear-gradient(180deg,#1a1a40,#0a0a2e);border:2px solid #00f0ff;border-radius:14px;padding:16px;text-align:center;}\n"
css += ".metric-label-retro{font-size:0.8rem;color:#8888cc;text-transform:uppercase;letter-spacing:2px;margin-bottom:6px;}\n"
css += ".metric-value-retro{font-size:2.2rem;font-weight:900;color:#00f0ff;text-shadow:0 0 15px rgba(0,240,255,0.5);}\n"
css += ".metric-value-gold{color:#ffd700;text-shadow:0 0 15px rgba(255,215,0,0.5);}\n"
css += ".metric-value-pink{color:#ff00aa;text-shadow:0 0 15px rgba(255,0,170,0.5);}\n"
css += ".prob-label-retro{display:flex;justify-content:space-between;font-size:0.9rem;color:#ccccff;margin-bottom:4px;font-weight:700;}\n"
css += ".prob-track-retro{width:100%;height:18px;background:#0a0a2e;border-radius:10px;border:1px solid #333366;overflow:hidden;margin-bottom:10px;}\n"
css += ".prob-fill-cyan{height:100%;background:linear-gradient(90deg,#004466,#00f0ff);border-radius:10px;box-shadow:0 0 10px rgba(0,240,255,0.4);}\n"
css += ".prob-fill-gold2{height:100%;background:linear-gradient(90deg,#665500,#ffd700);border-radius:10px;box-shadow:0 0 10px rgba(255,215,0,0.4);}\n"
css += ".prob-fill-pink{height:100%;background:linear-gradient(90deg,#660044,#ff00aa);border-radius:10px;box-shadow:0 0 10px rgba(255,0,170,0.4);}\n"
css += ".score-pill-retro{display:inline-block;padding:10px 16px;margin:5px;border-radius:12px;background:linear-gradient(180deg,#1a1a40,#0a0a2e);border:2px solid #00f0ff;font-weight:900;font-size:1.1rem;color:#00f0ff;text-shadow:0 0 8px rgba(0,240,255,0.4);}\n"
css += ".score-pill-top{border-color:#ffd700;color:#ffd700;text-shadow:0 0 8px rgba(255,215,0,0.4);font-size:1.3rem;animation:pulse 2s ease-in-out infinite;}\n"
css += ".star-player{display:inline-block;padding:6px 12px;margin:4px;border-radius:10px;background:linear-gradient(90deg,#1a1a40,#2a1a50);border:1px solid #ffd700;color:#ffd700;font-size:0.85rem;font-weight:700;}\n"
css += ".h2h-bar{display:flex;height:30px;border-radius:8px;overflow:hidden;margin:10px 0;border:1px solid #333366;}\n"
css += ".h2h-win{background:#00f0ff;}\n"
css += ".h2h-draw{background:#ffd700;}\n"
css += ".h2h-loss{background:#ff00aa;}\n"
css += ".insight-retro{border-left:4px solid #ffd700;background:linear-gradient(90deg,rgba(255,215,0,0.05),transparent);padding:14px 18px;border-radius:0 12px 12px 0;color:#ccccff;line-height:1.6;font-family:Trebuchet MS,sans-serif;}\n"
css += ".retro-divider{border:none;height:2px;background:linear-gradient(90deg,transparent,#00f0ff,#ffd700,#ff00aa,transparent);margin:1.2rem 0;}\n"
css += ".stButton>button{width:100%;background:linear-gradient(135deg,#ff6600,#ff0033);color:white;border:2px solid #ffd700;border-radius:14px;padding:0.8rem 1rem;font-weight:900;font-size:1rem;letter-spacing:1px;text-transform:uppercase;box-shadow:0 0 20px rgba(255,102,0,0.3);}\n"
css += ".stButton>button:hover{background:linear-gradient(135deg,#ff0033,#cc0066);color:white;border-color:#00f0ff;}\n"
css += ".stSelectbox label{color:#00f0ff !important;font-weight:700;text-transform:uppercase;letter-spacing:1px;}\n"
css += ".stCheckbox label{color:#ffd700 !important;font-weight:700;}\n"
css += '.stTabs [data-baseweb="tab-list"]{gap:4px;}\n'
css += '.stTabs [data-baseweb="tab"]{border-radius:12px 12px 0 0;padding:10px 16px;font-weight:700;color:#8888cc;background:#141430;border:1px solid #333366;}\n'
css += '.stTabs [aria-selected="true"]{background:#00f0ff !important;color:#0a0a2e !important;border-color:#00f0ff !important;}\n'
css += "</style>"

# 1: Replace CSS
s1 = content.find("<style>")
s2 = content.find("</style>") + len("</style>")
if s1 > -1:
    content = content[:s1] + css + content[s2:]
    print("  [1] CSS replaced")
    changes += 1

# 2: Replace classes
content = content.replace('class="card"', 'class="retro-card"')
content = content.replace('class="card-title"', 'class="retro-card-title"')
content = content.replace('class="insight"', 'class="insight-retro"')
print("  [2] Classes updated")
changes += 1

# 3: Replace dividers
content = content.replace(
    'st.markdown("<hr>", unsafe_allow_html=True)',
    "st.markdown('<div class=\"retro-divider\"></div>', unsafe_allow_html=True)"
)
print("  [3] Dividers updated")
changes += 1

# ==================== HELPERS ====================
helpers = '''

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
        return '<div style="color:#666688;font-style:italic;">\U0001f937 No previous meetings</div>'
    wa = result.get("h2h_wins_a", 0)
    wb = result.get("h2h_wins_b", 0)
    d = result.get("h2h_draws", 0)
    total = wa + wb + d
    if total == 0:
        total = 1
    pct_a = round(100 * wa / total)
    pct_d = round(100 * d / total)
    pct_b = 100 - pct_a - pct_d
    out = '<div style="color:#8888cc;margin-bottom:8px;">\U0001f4ca Last <b>' + str(matches) + '</b> meetings</div>'
    out += '<div class="h2h-bar">'
    if pct_a > 0:
        out += '<div class="h2h-win" style="width:' + str(pct_a) + '%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">' + str(wa) + 'W</div>'
    if pct_d > 0:
        out += '<div class="h2h-draw" style="width:' + str(pct_d) + '%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">' + str(d) + 'D</div>'
    if pct_b > 0:
        out += '<div class="h2h-loss" style="width:' + str(pct_b) + '%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">' + str(wb) + 'W</div>'
    out += '</div>'
    out += '<div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-top:4px;">'
    out += '<span style="color:#00f0ff;">\U0001f3c6 ' + team_a + '</span>'
    out += '<span style="color:#ffd700;">\U0001f91d Draw</span>'
    out += '<span style="color:#ff00aa;">\U0001f3c6 ' + team_b + '</span></div>'
    return out


'''

# 4: Add helpers before build_match_insight
marker = "def build_match_insight"
idx = content.find(marker)
if idx > -1:
    content = content[:idx] + helpers + content[idx:]
    print("  [4] Helpers added")
    changes += 1

# 5: Emoji-ify insight text
reps = [
    ('edge = team_a + " and " + team_b + " project as closely matched."',
     'edge = "\U0001f91c\U0001f91b " + team_a + " and " + team_b + " are neck and neck!"'),
    ('edge = team_a + " enter as the more likely winner."',
     'edge = "\U0001f4aa " + team_a + " have the edge."'),
    ('edge = team_b + " look slightly stronger in the current model."',
     'edge = "\U0001f4aa " + team_b + " look stronger."'),
    ('dr = "Draw probability is elevated, pointing to a compact match."',
     'dr = "\U0001f91d High draw probability!"'),
    ('dr = "Draw probability is modest, suggesting a decisive result."',
     'dr = "\u26a1 Low draw chance!"'),
    ('dr = "A draw remains a meaningful live outcome."',
     'dr = "\U0001f3b2 Draw still on the cards."'),
    ('gl = "Expected goals indicate a potentially open game."',
     'gl = "\U0001f525 Goals expected! Thriller alert!"'),
    ('gl = "Expected goals suggest a lower-scoring contest."',
     'gl = "\U0001f512 Tight game. Every goal matters."'),
    ('gl = "Expected goals point to a moderate scoring environment."',
     'gl = "\u26bd Balanced - 2-3 goals likely."'),
]
for old, new in reps:
    content = content.replace(old, new)
print("  [5] Insight emojis")
changes += 1

# 6: Replace badge call
content = content.replace(
    'st.markdown(badge_html(mt, "gold") + badge_html(vl, "green"), unsafe_allow_html=True)',
    'st.markdown(get_match_badge(mt) + get_venue_badge(neutral), unsafe_allow_html=True)'
)
print("  [6] Badges replaced")
changes += 1

# 7: Add stars + H2H before expected goals
cols_marker = "    s1, s2 = st.columns([1, 1])"
if cols_marker in content:
    inject = '''
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
    content = content.replace(cols_marker, inject + cols_marker)
    print("  [7] Stars + H2H added")
    changes += 1

# 8: Emoji titles
content = content.replace("Match Setup</div>", "\U0001f3ae Match Setup \U0001f3ae</div>", 1)
content = content.replace("Expected Goals</div>", "\u26bd Expected Goals \u26bd</div>")
content = content.replace("Most Likely Scorelines</div>", "\U0001f3af Top Scores \U0001f3af</div>")
content = content.replace("Model Insight</div>", "\U0001f9e0 AI Insight \U0001f9e0</div>")
content = content.replace("Visual Analytics</div>", "\U0001f4c8 Visual Analytics \U0001f4c8</div>")
content = content.replace("Win / Draw / Loss Profile</div>", "\U0001f4ca Win Probability \U0001f4ca</div>")
content = content.replace("How to use</div>", "\U0001f3ae How To Play \U0001f3ae</div>")
print("  [8] Title emojis")
changes += 1

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
new = len(content.splitlines())
print("\nDone! " + str(changes) + " changes, " + str(original) + " -> " + str(new) + " lines")
