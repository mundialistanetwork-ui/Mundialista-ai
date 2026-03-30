import matplotlib
matplotlib.use('Agg')

import streamlit as st
import pandas as pd
import os

from prediction_engine import predict, load_rankings
from chart_generator import generate_all_charts
from match_manager import show_recent, estimate_cards, ensure_files

st.set_page_config(
    page_title="Mundialista AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown('''
<style>
@keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.05);}}
@keyframes marquee{0%{transform:translateX(100%);}100%{transform:translateX(-100%);}}
html,body,[class*="css"]{font-family:Impact,Arial Black,Trebuchet MS,sans-serif;}
.main{background:linear-gradient(180deg,#0a0a2e,#1a0a3e,#0a1a2e);color:#e0e0ff;}
.block-container{padding-top:1rem;padding-bottom:2rem;max-width:1200px;}
.retro-card{background:linear-gradient(180deg,#141430,#1a1a40);border:2px solid #00f0ff;border-radius:16px;padding:22px;margin-bottom:1rem;box-shadow:0 0 15px rgba(0,240,255,0.15);}
.retro-card-title{font-size:1.2rem;font-weight:900;color:#ffd700;text-shadow:1px 1px 0 #ff6600;margin-bottom:12px;letter-spacing:1px;text-transform:uppercase;}
.retro-card-pink{border-color:#ff00aa;box-shadow:0 0 15px rgba(255,0,170,0.15);}
.retro-card-green{border-color:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.15);}
.retro-card-gold{border-color:#ffd700;box-shadow:0 0 15px rgba(255,215,0,0.15);}
.vs-retro{display:flex;align-items:center;justify-content:space-between;padding:10px 0;}
.team-retro{font-size:1.5rem;font-weight:900;color:#00f0ff;text-shadow:0 0 10px rgba(0,240,255,0.5);}
.team-rank-retro{color:#8888aa;font-size:0.85rem;font-family:"Courier New",monospace;}
.vs-badge{font-size:1.4rem;font-weight:900;color:#ffd700;text-shadow:2px 2px 0 #ff6600;padding:8px 16px;border:2px solid #ffd700;border-radius:50%;background:rgba(255,215,0,0.1);animation:pulse 2s ease-in-out infinite;}
.match-badge{display:inline-block;padding:8px 16px;border-radius:20px;font-size:0.9rem;font-weight:900;margin:6px 8px 6px 0;letter-spacing:1px;text-transform:uppercase;}
.badge-elite{background:linear-gradient(90deg,#ff6600,#ff0033);color:white;border:2px solid #ff0033;animation:pulse 2s ease-in-out infinite;}
.badge-mismatch{background:linear-gradient(90deg,#8b0000,#4a0000);color:#ff6666;border:2px solid #ff3333;}
.badge-favorite{background:linear-gradient(90deg,#004e92,#0066cc);color:#88ccff;border:2px solid #00aaff;}
.badge-competitive{background:linear-gradient(90deg,#006644,#00aa66);color:#88ffcc;border:2px solid #00ff88;}
.badge-venue{background:rgba(255,215,0,0.15);color:#ffd700;border:2px solid #ffd700;}
.metric-retro{display:flex;gap:16px;flex-wrap:wrap;margin:12px 0;}
.metric-box-retro{flex:1;min-width:140px;background:linear-gradient(180deg,#1a1a40,#0a0a2e);border:2px solid #00f0ff;border-radius:14px;padding:16px;text-align:center;}
.metric-label-retro{font-size:0.8rem;color:#8888cc;text-transform:uppercase;letter-spacing:2px;margin-bottom:6px;}
.metric-value-retro{font-size:2.2rem;font-weight:900;color:#00f0ff;text-shadow:0 0 15px rgba(0,240,255,0.5);}
.metric-value-gold{color:#ffd700;text-shadow:0 0 15px rgba(255,215,0,0.5);}
.metric-value-pink{color:#ff00aa;text-shadow:0 0 15px rgba(255,0,170,0.5);}
.prob-label-retro{display:flex;justify-content:space-between;font-size:0.9rem;color:#ccccff;margin-bottom:4px;font-weight:700;}
.prob-track-retro{width:100%;height:18px;background:#0a0a2e;border-radius:10px;border:1px solid #333366;overflow:hidden;margin-bottom:10px;}
.prob-fill-cyan{height:100%;background:linear-gradient(90deg,#004466,#00f0ff);border-radius:10px;box-shadow:0 0 10px rgba(0,240,255,0.4);}
.prob-fill-gold2{height:100%;background:linear-gradient(90deg,#665500,#ffd700);border-radius:10px;box-shadow:0 0 10px rgba(255,215,0,0.4);}
.prob-fill-pink{height:100%;background:linear-gradient(90deg,#660044,#ff00aa);border-radius:10px;box-shadow:0 0 10px rgba(255,0,170,0.4);}
.score-pill-retro{display:inline-block;padding:10px 16px;margin:5px;border-radius:12px;background:linear-gradient(180deg,#1a1a40,#0a0a2e);border:2px solid #00f0ff;font-weight:900;font-size:1.1rem;color:#00f0ff;text-shadow:0 0 8px rgba(0,240,255,0.4);}
.score-pill-top{border-color:#ffd700;color:#ffd700;text-shadow:0 0 8px rgba(255,215,0,0.4);font-size:1.3rem;animation:pulse 2s ease-in-out infinite;}
.star-player{display:inline-block;padding:6px 12px;margin:4px;border-radius:10px;background:linear-gradient(90deg,#1a1a40,#2a1a50);border:1px solid #ffd700;color:#ffd700;font-size:0.85rem;font-weight:700;}
.h2h-bar{display:flex;height:30px;border-radius:8px;overflow:hidden;margin:10px 0;border:1px solid #333366;}
.h2h-win{background:#00f0ff;}
.h2h-draw{background:#ffd700;}
.h2h-loss{background:#ff00aa;}
.insight-retro{border-left:4px solid #ffd700;background:linear-gradient(90deg,rgba(255,215,0,0.05),transparent);padding:14px 18px;border-radius:0 12px 12px 0;color:#ccccff;line-height:1.6;font-family:Trebuchet MS,sans-serif;}
.retro-divider{border:none;height:2px;background:linear-gradient(90deg,transparent,#00f0ff,#ffd700,#ff00aa,transparent);margin:1.2rem 0;}
.stButton>button{width:100%;background:linear-gradient(135deg,#ff6600,#ff0033);color:white;border:2px solid #ffd700;border-radius:14px;padding:0.8rem 1rem;font-weight:900;font-size:1rem;letter-spacing:1px;text-transform:uppercase;box-shadow:0 0 20px rgba(255,102,0,0.3);}
.stButton>button:hover{background:linear-gradient(135deg,#ff0033,#cc0066);color:white;border-color:#00f0ff;}
.stSelectbox label{color:#00f0ff !important;font-weight:700;text-transform:uppercase;letter-spacing:1px;}
.stCheckbox label{color:#ffd700 !important;font-weight:700;}
.stTabs [data-baseweb="tab-list"]{gap:4px;}
.stTabs [data-baseweb="tab"]{border-radius:12px 12px 0 0;padding:10px 16px;font-weight:700;color:#8888cc;background:#141430;border:1px solid #333366;}
.stTabs [aria-selected="true"]{background:#00f0ff !important;color:#0a0a2e !important;border-color:#00f0ff !important;}
</style>
''', unsafe_allow_html=True)


@st.cache_data
def get_team_list():
    rankings = load_rankings()
    if isinstance(rankings, pd.DataFrame):
        if "country_full" in rankings.columns:
            return sorted(rankings["country_full"].dropna().unique().tolist())
    return []


def badge_html(text, kind="green"):
    klass = {"green": "badge badge-green", "gold": "badge badge-gold", "gray": "badge badge-gray"}.get(kind, "badge badge-green")
    return '<span class="' + klass + '">' + text + '</span>'




def get_match_badge(match_type):
    badges = {
        "Elite Clash": '<span class="match-badge badge-elite">⚔️🔥 ELITE CLASH 🔥⚔️</span>',
        "Total Mismatch": '<span class="match-badge badge-mismatch">💀 TOTAL MISMATCH 💀</span>',
        "Clear Favorite": '<span class="match-badge badge-favorite">👑 CLEAR FAVORITE 👑</span>',
        "Competitive Match": '<span class="match-badge badge-competitive">⚡ COMPETITIVE ⚡</span>',
    }
    return badges.get(match_type, '<span class="match-badge badge-competitive">⚽ MATCH ⚽</span>')


def get_venue_badge(neutral):
    if neutral:
        return '<span class="match-badge badge-venue">🏟️ NEUTRAL 🏟️</span>'
    return '<span class="match-badge badge-venue">🏠 HOME ADVANTAGE 🏠</span>'


def build_stars_html(players, boost):
    if not players:
        return '<div style="color:#666688;font-style:italic;">No star data</div>'
    h = '<div style="margin-bottom:6px;color:#ffd700;font-weight:700;">⭐ Boost: x' + str(boost) + '</div>'
    for p in players[:5]:
        h += '<span class="star-player">🌟 ' + str(p) + '</span>'
    return h


def build_h2h_html(result, team_a, team_b):
    matches = result.get("h2h_matches", 0)
    if matches == 0:
        return '<div style="color:#666688;font-style:italic;">🤷 No previous meetings</div>'
    wa = result.get("h2h_wins_a", 0)
    wb = result.get("h2h_wins_b", 0)
    d = result.get("h2h_draws", 0)
    total = wa + wb + d
    if total == 0:
        total = 1
    pct_a = round(100 * wa / total)
    pct_d = round(100 * d / total)
    pct_b = 100 - pct_a - pct_d
    out = '<div style="color:#8888cc;margin-bottom:8px;">📊 Last <b>' + str(matches) + '</b> meetings</div>'
    out += '<div class="h2h-bar">'
    if pct_a > 0:
        out += '<div class="h2h-win" style="width:' + str(pct_a) + '%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">' + str(wa) + 'W</div>'
    if pct_d > 0:
        out += '<div class="h2h-draw" style="width:' + str(pct_d) + '%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">' + str(d) + 'D</div>'
    if pct_b > 0:
        out += '<div class="h2h-loss" style="width:' + str(pct_b) + '%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">' + str(wb) + 'W</div>'
    out += '</div>'
    out += '<div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-top:4px;">'
    out += '<span style="color:#00f0ff;">🏆 ' + team_a + '</span>'
    out += '<span style="color:#ffd700;">🤝 Draw</span>'
    out += '<span style="color:#ff00aa;">🏆 ' + team_b + '</span></div>'
    return out


def build_match_insight(result, team_a, team_b):
    a = result["team_a_win"]
    d = result["draw"]
    b = result["team_b_win"]
    la = result["team_a_lambda"]
    lb = result["team_b_lambda"]
    mt = result.get("match_type", "Competitive")
    if abs(a - b) <= 6:
        edge = "🤜🤛 " + team_a + " and " + team_b + " are neck and neck!"
    elif a > b:
        edge = "💪 " + team_a + " have the edge."
    else:
        edge = "💪 " + team_b + " look stronger."
    if d >= 27:
        dr = "🤝 High draw probability!"
    elif d <= 20:
        dr = "⚡ Low draw chance!"
    else:
        dr = "🎲 Draw still on the cards."
    if la + lb >= 2.9:
        gl = "🔥 Goals expected! Thriller alert!"
    elif la + lb <= 2.3:
        gl = "🔒 Tight game. Every goal matters."
    else:
        gl = "⚽ Balanced - 2-3 goals likely."
    return mt + ". " + edge + " " + dr + " " + gl


teams = get_team_list()

st.markdown('''
<div class="hero">
    <div class="hero-title">Mundialista AI</div>
    <div class="hero-subtitle">International Match Intelligence</div>
    <div class="hero-tag">Refined match predictions - Global national teams - Visual-first analytics</div>
</div>
''', unsafe_allow_html=True)

st.markdown('<div class="retro-card"><div class="retro-card-title">🎮 Match Setup 🎮</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 0.6])
with col1:
    team_a = st.selectbox("Home / Team A", teams, index=teams.index("Argentina") if "Argentina" in teams else 0)
with col2:
    default_b = teams.index("Brazil") if "Brazil" in teams else (1 if len(teams) > 1 else 0)
    team_b = st.selectbox("Away / Team B", teams, index=default_b)
with col3:
    neutral = st.checkbox("Neutral venue", value=True)
    run_prediction = st.button("Generate Prediction")
st.markdown('</div>', unsafe_allow_html=True)

if run_prediction:
    if team_a == team_b:
        st.warning("Please choose two different teams.")
    else:
        try:
            with st.spinner("Generating prediction and charts..."):
                result = predict(team_a, team_b)
                charts = generate_all_charts(result, team_a, team_b)
                st.session_state["result"] = result
                st.session_state["charts"] = charts
                st.session_state["pred_a"] = team_a
                st.session_state["pred_b"] = team_b
        except Exception as e:
            st.error("Prediction failed: " + str(e))

if "result" in st.session_state:
    result = st.session_state["result"]
    charts = st.session_state["charts"]
    da = st.session_state["pred_a"]
    db = st.session_state["pred_b"]
    rk_a = result.get("team_a_rank", "N/A")
    rk_b = result.get("team_b_rank", "N/A")
    la = result.get("team_a_lambda", 0.0)
    lb = result.get("team_b_lambda", 0.0)
    mt = result.get("match_type", "Competitive")
    ts = result.get("top_scores", [])[:5]
    wa = "{:.1f}".format(result["team_a_win"])
    dv = "{:.1f}".format(result["draw"])
    wb = "{:.1f}".format(result["team_b_win"])
    la_s = "{:.2f}".format(la)
    lb_s = "{:.2f}".format(lb)

    st.markdown('<div class="retro-card">', unsafe_allow_html=True)
    v = '<div class="vs-line"><div><div class="team-name">' + da + '</div>'
    v += '<div class="team-rank">FIFA Rank: ' + str(rk_a) + '</div></div>'
    v += '<div class="vs-center">VS</div>'
    v += '<div style="text-align:right;"><div class="team-name">' + db + '</div>'
    v += '<div class="team-rank">FIFA Rank: ' + str(rk_b) + '</div></div></div>'
    st.markdown(v, unsafe_allow_html=True)

    vl = "Neutral Venue" if neutral else "Home Advantage Active"
    st.markdown(get_match_badge(mt) + get_venue_badge(neutral), unsafe_allow_html=True)

    m = '<div class="metric-row">'
    m += '<div class="metric-box"><div class="metric-label">' + da + ' Win</div>'
    m += '<div class="metric-value">' + wa + '%</div>'
    m += '<div class="metric-sub">Model win probability</div></div>'
    m += '<div class="metric-box"><div class="metric-label">Draw</div>'
    m += '<div class="metric-value" style="color:#8A6B00;">' + dv + '%</div>'
    m += '<div class="metric-sub">Shared outcome probability</div></div>'
    m += '<div class="metric-box"><div class="metric-label">' + db + ' Win</div>'
    m += '<div class="metric-value">' + wb + '%</div>'
    m += '<div class="metric-sub">Model win probability</div></div></div>'
    st.markdown(m, unsafe_allow_html=True)

    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="retro-card-title">📊 Win Probability 📊</div>', unsafe_allow_html=True)
    p = '<div class="prob-wrap">'
    p += '<div class="prob-label-row"><span>' + da + ' win</span><span>' + wa + '%</span></div>'
    p += '<div class="prob-track"><div class="prob-fill-green" style="width:' + wa + '%;"></div></div>'
    p += '<div class="prob-label-row"><span>Draw</span><span>' + dv + '%</span></div>'
    p += '<div class="prob-track"><div class="prob-fill-gold" style="width:' + dv + '%;"></div></div>'
    p += '<div class="prob-label-row"><span>' + db + ' win</span><span>' + wb + '%</span></div>'
    p += '<div class="prob-track"><div class="prob-fill-gray" style="width:' + wb + '%;"></div></div></div>'
    st.markdown(p, unsafe_allow_html=True)

    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown('<div class="retro-card retro-card-gold"><div class="retro-card-title">🌟 ' + da + ' Stars 🌟</div>', unsafe_allow_html=True)
        st.markdown(build_stars_html(result.get("team_a_stars", []), result.get("team_a_star_boost", 1.0)), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with sc2:
        st.markdown('<div class="retro-card retro-card-gold"><div class="retro-card-title">🌟 ' + db + ' Stars 🌟</div>', unsafe_allow_html=True)
        st.markdown(build_stars_html(result.get("team_b_stars", []), result.get("team_b_star_boost", 1.0)), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="retro-card retro-card-pink"><div class="retro-card-title">⚔️ Head-to-Head ⚔️</div>', unsafe_allow_html=True)
    st.markdown(build_h2h_html(result, da, db), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    s1, s2 = st.columns([1, 1])
    with s1:
        st.markdown('<div class="retro-card-title">⚽ Expected Goals ⚽</div>', unsafe_allow_html=True)
        x = '<div class="metric-row">'
        x += '<div class="metric-box"><div class="metric-label">' + da + '</div>'
        x += '<div class="metric-value">' + la_s + '</div>'
        x += '<div class="metric-sub">Expected goals</div></div>'
        x += '<div class="metric-box"><div class="metric-label">' + db + '</div>'
        x += '<div class="metric-value">' + lb_s + '</div>'
        x += '<div class="metric-sub">Expected goals</div></div></div>'
        st.markdown(x, unsafe_allow_html=True)
    with s2:
        st.markdown('<div class="retro-card-title">🎯 Top Scores 🎯</div>', unsafe_allow_html=True)
        if ts:
            sh = ""
            for sc in ts:
                if isinstance(sc, (list, tuple)) and len(sc) >= 2:
                    sh += '<span class="score-pill">' + str(sc[0]) + ' - ' + str(sc[1]) + '</span>'
                else:
                    sh += '<span class="score-pill">' + str(sc) + '</span>'
            st.markdown(sh, unsafe_allow_html=True)
        else:
            st.markdown('<div class="muted">No scoreline data.</div>', unsafe_allow_html=True)

    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)
    ins = build_match_insight(result, da, db)
    st.markdown('<div class="retro-card-title">🧠 AI Insight 🧠</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-retro">' + ins + '</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="retro-card"><div class="retro-card-title">📈 Visual Analytics 📈</div>', unsafe_allow_html=True)
    t1, t2, t3, t4, t5 = st.tabs(["Summary Card", "Win Probability", "Score Matrix", "Top Scorelines", "Goal Distribution"])
    with t1:
        if "summary" in charts and os.path.exists(charts["summary"]):
            st.image(charts["summary"], width='stretch')
        else:
            st.info("Summary chart not available.")
    with t2:
        if "probability" in charts and os.path.exists(charts["probability"]):
            st.image(charts["probability"], width='stretch')
        else:
            st.info("Probability chart not available.")
    with t3:
        if "matrix" in charts and os.path.exists(charts["matrix"]):
            st.image(charts["matrix"], width='stretch')
        else:
            st.info("Score matrix not available.")
    with t4:
        if "top_scores" in charts and os.path.exists(charts["top_scores"]):
            st.image(charts["top_scores"], width='stretch')
        else:
            st.info("Top scores chart not available.")
    with t5:
        if "goals" in charts and os.path.exists(charts["goals"]):
            st.image(charts["goals"], width='stretch')
        else:
            st.info("Goal distribution not available.")
    st.markdown('</div>', unsafe_allow_html=True)

    if "html" in charts and os.path.exists(charts["html"]):
        with open(charts["html"], "r", encoding="utf-8") as f:
            hc = f.read()
        st.download_button(label="Download Full HTML Report", data=hc, file_name=os.path.basename(charts["html"]), mime="text/html")

    with st.expander("Raw prediction output"):
        st.json(result)




else:
    st.markdown('''
    <div class="retro-card">
        <div class="retro-card-title">🎮 How To Play 🎮</div>
        <div class="muted">
            Select two national teams, choose whether the match is on neutral ground, and click
            <strong>Generate Prediction</strong> to view win probabilities, expected goals, likely scorelines,
            model-generated match insight, and full visual analytics charts.
        </div>
    </div>
    ''', unsafe_allow_html=True)

# === SIDEBAR: Admin Panel ===
with st.sidebar:
    st.markdown('<div class="retro-card-title">🛠️ Admin Panel 🛠️</div>', unsafe_allow_html=True)

    with st.expander("➕ Add Recent Result"):
        ensure_files()
        import pandas as pd_admin
        ad_date = st.text_input("Date (YYYY-MM-DD)", value=str(pd.Timestamp.now().date()))
        ad_col1, ad_col2 = st.columns(2)
        with ad_col1:
            ad_home = st.text_input("Home team")
            ad_hscore = st.number_input("Home score", min_value=0, max_value=20, value=0)
        with ad_col2:
            ad_away = st.text_input("Away team")
            ad_ascore = st.number_input("Away score", min_value=0, max_value=20, value=0)
        ad_tourn = st.selectbox("Tournament", [
            "FIFA World Cup qualification",
            "FIFA World Cup",
            "Friendly",
            "UEFA Euro",
            "Copa America",
            "UEFA Nations League",
            "Africa Cup of Nations",
            "AFC Asian Cup",
            "CONCACAF Gold Cup",
        ])
        ad_neutral = st.checkbox("Neutral venue", value=False, key="admin_neutral")

        if st.button("💾 Save Result"):
            if ad_home and ad_away:
                import pandas as pd_save
                try:
                    rdf = pd_save.read_csv("data/recent_results.csv")
                except FileNotFoundError:
                    rdf = pd_save.DataFrame(columns=["date","home_team","away_team","home_score","away_score","tournament","city","country","neutral"])
                new_row = pd_save.DataFrame([{
                    "date": ad_date, "home_team": ad_home, "away_team": ad_away,
                    "home_score": int(ad_hscore), "away_score": int(ad_ascore),
                    "tournament": ad_tourn, "city": "", "country": "", "neutral": ad_neutral,
                }])
                rdf = pd_save.concat([rdf, new_row], ignore_index=True)
                rdf.to_csv("data/recent_results.csv", index=False)
                try:
                    from prediction_engine import clear_cache
                    clear_cache()
                except Exception:
                    pass
                st.success("✅ " + ad_home + " " + str(int(ad_hscore)) + "-" + str(int(ad_ascore)) + " " + ad_away + " saved!")
            else:
                st.warning("Enter both team names!")

    with st.expander("📋 View Recent Results"):
        try:
            rdf_view = pd.read_csv("data/recent_results.csv")
            if rdf_view.empty:
                st.info("No recent results yet.")
            else:
                for _, rv in rdf_view.iterrows():
                    st.markdown(
                        '<span style="color:#00f0ff;">' + str(rv["date"]) + '</span> '
                        + '<b style="color:#ffd700;">' + str(rv["home_team"]) + ' ' + str(rv["home_score"]) + '-' + str(rv["away_score"]) + ' ' + str(rv["away_team"]) + '</b> '
                        + '<span style="color:#8888cc;">[' + str(rv["tournament"]) + ']</span>',
                        unsafe_allow_html=True
                    )
        except FileNotFoundError:
            st.info("No recent results file.")

    with st.expander("🟥 Card Predictor"):
        cp_col1, cp_col2 = st.columns(2)
        with cp_col1:
            cp_a = st.selectbox("Team A", teams, index=0, key="card_a")
        with cp_col2:
            cp_b_idx = 1 if len(teams) > 1 else 0
            cp_b = st.selectbox("Team B", teams, index=cp_b_idx, key="card_b")
        if st.button("🟥 Predict Cards"):
            if cp_a != cp_b:
                try:
                    from prediction_engine import get_team_stats, get_team_ranking
                    s_a = get_team_stats(cp_a)
                    s_b = get_team_stats(cp_b)
                    r_a = get_team_ranking(cp_a)
                    r_b = get_team_ranking(cp_b)
                    rank_gap = abs(r_a - r_b)
                    if rank_gap > 50:
                        intensity = 0.85
                    elif rank_gap < 15:
                        intensity = 1.25
                    else:
                        intensity = 1.0
                    base_yellow = 2.8
                    agg_a = s_a.get("defense", 1.0) * 0.6 + s_a.get("avg_ga", 1.36) * 0.2
                    agg_b = s_b.get("defense", 1.0) * 0.6 + s_b.get("avg_ga", 1.36) * 0.2
                    y_a = base_yellow * 0.5 * intensity * agg_a
                    y_b = base_yellow * 0.5 * intensity * agg_b
                    total_y = y_a + y_b
                    red_factor = intensity
                    if total_y > 4.0:
                        red_factor *= 1.3
                    red_prob = min(0.08 * red_factor * 2 * 4, 0.35)
                    st.markdown('<div class="retro-card">', unsafe_allow_html=True)
                    st.markdown('<div class="retro-card-title">🟥 Card Forecast 🟥</div>', unsafe_allow_html=True)
                    st.markdown(
                        '🟨 <b style="color:#ffd700;">' + cp_a + '</b>: ~' + str(round(y_a, 1)) + ' yellows<br>'
                        + '🟨 <b style="color:#ffd700;">' + cp_b + '</b>: ~' + str(round(y_b, 1)) + ' yellows<br>'
                        + '🟨 Total: ~' + str(round(total_y, 1)) + ' yellows<br>'
                        + '🟥 Red probability: <b>' + str(round(100 * red_prob, 1)) + '%</b>',
                        unsafe_allow_html=True
                    )
                    if red_prob > 0.25:
                        st.markdown('🟥 <b style="color:#ff3333;">HIGH red card risk! Heated match!</b>', unsafe_allow_html=True)
                    elif red_prob > 0.15:
                        st.markdown('🟨 <b style="color:#ffd700;">Moderate red card risk.</b>', unsafe_allow_html=True)
                    else:
                        st.markdown('🟩 <b style="color:#00ff88;">Low red card risk.</b>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error("Error: " + str(e))

    with st.expander("🗑️ Clear Recent Data"):
        if st.button("Clear ALL recent results"):
            pd.DataFrame(columns=["date","home_team","away_team","home_score","away_score","tournament","city","country","neutral"]).to_csv("data/recent_results.csv", index=False)
            pd.DataFrame(columns=["date","home_team","away_team","team","scorer","minute","own_goal","penalty"]).to_csv("data/recent_goalscorers.csv", index=False)
            try:
                from prediction_engine import clear_cache
                clear_cache()
            except Exception:
                pass
            st.success("🗑️ All recent data cleared!")


