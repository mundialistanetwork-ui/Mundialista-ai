with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
if content.startswith('\ufeff'):
    content = content[1:]
original_len = len(content.splitlines())
changes = 0

# === 1: Replace CSS ===
old_css_start = content.find("<style>")
old_css_end = content.find("</style>") + len("</style>")

retro_css = '<style>\n'
retro_css += '@keyframes pulse { 0%%,100%%{transform:scale(1);} 50%%{transform:scale(1.05);} }\n'
retro_css += '@keyframes marquee { 0%%{transform:translateX(100%%);} 100%%{transform:translateX(-100%%);} }\n'
retro_css += 'html, body, [class*="css"] { font-family:"Impact","Arial Black","Trebuchet MS",sans-serif; }\n'
retro_css += '.main { background:linear-gradient(180deg,#0a0a2e 0%%,#1a0a3e 50%%,#0a1a2e 100%%); color:#e0e0ff; }\n'
retro_css += '.block-container { padding-top:1rem; padding-bottom:2rem; max-width:1200px; }\n'
retro_css += '.hero-retro { background:linear-gradient(135deg,#000428 0%%,#004e92 50%%,#000428 100%%); border:3px solid #00f0ff; border-radius:20px; padding:30px; margin-bottom:1.5rem; text-align:center; box-shadow:0 0 30px rgba(0,240,255,0.3),inset 0 0 30px rgba(0,240,255,0.1); overflow:hidden; }\n'
retro_css += '.hero-title-retro { font-size:3rem; font-weight:900; color:#ffd700; text-shadow:3px 3px 0px #ff6600,0 0 20px rgba(255,215,0,0.5); letter-spacing:2px; }\n'
retro_css += '.hero-sub-retro { font-size:1.1rem; color:#00f0ff; text-shadow:0 0 10px #00f0ff; letter-spacing:3px; text-transform:uppercase; }\n'
retro_css += '.hero-marquee { margin-top:12px; overflow:hidden; white-space:nowrap; }\n'
retro_css += '.hero-marquee span { display:inline-block; animation:marquee 15s linear infinite; font-size:0.9rem; color:#ff00aa; }\n'
retro_css += '.retro-card { background:linear-gradient(180deg,#141430 0%%,#1a1a40 100%%); border:2px solid #00f0ff; border-radius:16px; padding:22px; margin-bottom:1rem; box-shadow:0 0 15px rgba(0,240,255,0.15); }\n'
retro_css += '.retro-card-title { font-size:1.2rem; font-weight:900; color:#ffd700; text-shadow:1px 1px 0 #ff6600; margin-bottom:12px; letter-spacing:1px; text-transform:uppercase; }\n'
retro_css += '.retro-card-pink { border-color:#ff00aa; box-shadow:0 0 15px rgba(255,0,170,0.15); }\n'
retro_css += '.retro-card-green { border-color:#00ff88; box-shadow:0 0 15px rgba(0,255,136,0.15); }\n'
retro_css += '.retro-card-gold { border-color:#ffd700; box-shadow:0 0 15px rgba(255,215,0,0.15); }\n'
retro_css += '.vs-retro { display:flex; align-items:center; justify-content:space-between; padding:10px 0; }\n'
retro_css += '.team-retro { font-size:1.5rem; font-weight:900; color:#00f0ff; text-shadow:0 0 10px rgba(0,240,255,0.5); }\n'
retro_css += '.team-rank-retro { color:#8888aa; font-size:0.85rem; font-family:"Courier New",monospace; }\n'
retro_css += '.vs-badge { font-size:1.4rem; font-weight:900; color:#ffd700; text-shadow:2px 2px 0 #ff6600; padding:8px 16px; border:2px solid #ffd700; border-radius:50%%; background:rgba(255,215,0,0.1); animation:pulse 2s ease-in-out infinite; }\n'
retro_css += '.match-badge { display:inline-block; padding:8px 16px; border-radius:20px; font-size:0.9rem; font-weight:900; margin:6px 8px 6px 0; letter-spacing:1px; text-transform:uppercase; }\n'
retro_css += '.badge-elite { background:linear-gradient(90deg,#ff6600,#ff0033); color:white; border:2px solid #ff0033; animation:pulse 2s ease-in-out infinite; }\n'
retro_css += '.badge-mismatch { background:linear-gradient(90deg,#8b0000,#4a0000); color:#ff6666; border:2px solid #ff3333; }\n'
retro_css += '.badge-favorite { background:linear-gradient(90deg,#004e92,#0066cc); color:#88ccff; border:2px solid #00aaff; }\n'
retro_css += '.badge-competitive { background:linear-gradient(90deg,#006644,#00aa66); color:#88ffcc; border:2px solid #00ff88; }\n'
retro_css += '.badge-venue { background:rgba(255,215,0,0.15); color:#ffd700; border:2px solid #ffd700; }\n'
retro_css += '.metric-retro { display:flex; gap:16px; flex-wrap:wrap; margin:12px 0; }\n'
retro_css += '.metric-box-retro { flex:1; min-width:140px; background:linear-gradient(180deg,#1a1a40 0%%,#0a0a2e 100%%); border:2px solid #00f0ff; border-radius:14px; padding:16px; text-align:center; }\n'
retro_css += '.metric-label-retro { font-size:0.8rem; color:#8888cc; text-transform:uppercase; letter-spacing:2px; margin-bottom:6px; }\n'
retro_css += '.metric-value-retro { font-size:2.2rem; font-weight:900; color:#00f0ff; text-shadow:0 0 15px rgba(0,240,255,0.5); }\n'
retro_css += '.metric-value-gold { color:#ffd700; text-shadow:0 0 15px rgba(255,215,0,0.5); }\n'
retro_css += '.metric-value-pink { color:#ff00aa; text-shadow:0 0 15px rgba(255,0,170,0.5); }\n'
retro_css += '.prob-label-retro { display:flex; justify-content:space-between; font-size:0.9rem; color:#ccccff; margin-bottom:4px; font-weight:700; }\n'
retro_css += '.prob-track-retro { width:100%%; height:18px; background:#0a0a2e; border-radius:10px; border:1px solid #333366; overflow:hidden; margin-bottom:10px; }\n'
retro_css += '.prob-fill-cyan { height:100%%; background:linear-gradient(90deg,#004466,#00f0ff); border-radius:10px; box-shadow:0 0 10px rgba(0,240,255,0.4); }\n'
retro_css += '.prob-fill-gold2 { height:100%%; background:linear-gradient(90deg,#665500,#ffd700); border-radius:10px; box-shadow:0 0 10px rgba(255,215,0,0.4); }\n'
retro_css += '.prob-fill-pink { height:100%%; background:linear-gradient(90deg,#660044,#ff00aa); border-radius:10px; box-shadow:0 0 10px rgba(255,0,170,0.4); }\n'
retro_css += '.score-pill-retro { display:inline-block; padding:10px 16px; margin:5px; border-radius:12px; background:linear-gradient(180deg,#1a1a40,#0a0a2e); border:2px solid #00f0ff; font-weight:900; font-size:1.1rem; color:#00f0ff; text-shadow:0 0 8px rgba(0,240,255,0.4); }\n'
retro_css += '.score-pill-top { border-color:#ffd700; color:#ffd700; text-shadow:0 0 8px rgba(255,215,0,0.4); font-size:1.3rem; animation:pulse 2s ease-in-out infinite; }\n'
retro_css += '.star-player { display:inline-block; padding:6px 12px; margin:4px; border-radius:10px; background:linear-gradient(90deg,#1a1a40,#2a1a50); border:1px solid #ffd700; color:#ffd700; font-size:0.85rem; font-weight:700; }\n'
retro_css += '.h2h-bar { display:flex; height:30px; border-radius:8px; overflow:hidden; margin:10px 0; border:1px solid #333366; }\n'
retro_css += '.h2h-win { background:#00f0ff; }\n'
retro_css += '.h2h-draw { background:#ffd700; }\n'
retro_css += '.h2h-loss { background:#ff00aa; }\n'
retro_css += '.insight-retro { border-left:4px solid #ffd700; background:linear-gradient(90deg,rgba(255,215,0,0.05),transparent); padding:14px 18px; border-radius:0 12px 12px 0; color:#ccccff; line-height:1.6; font-family:"Trebuchet MS",sans-serif; }\n'
retro_css += '.retro-divider { border:none; height:2px; background:linear-gradient(90deg,transparent,#00f0ff,#ffd700,#ff00aa,transparent); margin:1.2rem 0; }\n'
retro_css += '.stButton > button { width:100%%; background:linear-gradient(135deg,#ff6600 0%%,#ff0033 100%%); color:white; border:2px solid #ffd700; border-radius:14px; padding:0.8rem 1rem; font-weight:900; font-size:1rem; letter-spacing:1px; text-transform:uppercase; box-shadow:0 0 20px rgba(255,102,0,0.3); }\n'
retro_css += '.stButton > button:hover { background:linear-gradient(135deg,#ff0033 0%%,#cc0066 100%%); color:white; border-color:#00f0ff; }\n'
retro_css += '.stSelectbox label { color:#00f0ff !important; font-weight:700; text-transform:uppercase; letter-spacing:1px; }\n'
retro_css += '.stCheckbox label { color:#ffd700 !important; font-weight:700; }\n'
retro_css += '.stTabs [data-baseweb="tab-list"] { gap:4px; }\n'
retro_css += '.stTabs [data-baseweb="tab"] { border-radius:12px 12px 0 0; padding:10px 16px; font-weight:700; color:#8888cc; background:#141430; border:1px solid #333366; }\n'
retro_css += '.stTabs [aria-selected="true"] { background:#00f0ff !important; color:#0a0a2e !important; border-color:#00f0ff !important; }\n'
retro_css += '</style>'

if old_css_start > -1 and old_css_end > old_css_start:
    content = content[:old_css_start] + retro_css + content[old_css_end:]
    print("  [1] CSS replaced with retro theme")
    changes += 1

# === 2: Replace card/class names ===
content = content.replace('class="card"', 'class="retro-card"')
content = content.replace('class="card-title"', 'class="retro-card-title"')
print("  [2] Card classes updated")
changes += 1

# === 3: Replace hr with retro divider ===
content = content.replace(
    'st.markdown("<hr>", unsafe_allow_html=True)',
    "st.markdown('<div class=" + '"retro-divider"></div>' + "', unsafe_allow_html=True)"
)
print("  [3] Dividers updated")
changes += 1

# === 4: Replace insight class ===
content = content.replace('class="insight"', 'class="insight-retro"')
print("  [4] Insight class updated")
changes += 1

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
new_len = len(content.splitlines())
print("\nPart 1 done: " + str(changes) + " changes, " + str(original_len) + " -> " + str(new_len) + " lines")
