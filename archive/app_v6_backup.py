import matplotlib
matplotlib.use('Agg')

import streamlit as st
import pandas as pd
import os

from prediction_engine import predict, load_rankings
from chart_generator import generate_all_charts

st.set_page_config(
    page_title="Mundialista AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown('''
<style>
:root {
    --green: #0F5C4D;
    --green-2: #0B6B57;
    --gold: #C9A227;
    --ivory: #F8F7F2;
    --white: #FFFFFF;
    --text: #1E1E1E;
    --muted: #6B7280;
    --border: rgba(15, 92, 77, 0.12);
    --shadow: 0 6px 22px rgba(0, 0, 0, 0.05);
    --radius: 18px;
}
html, body, [class*="css"] { font-family: "Segoe UI", "Inter", sans-serif; }
.main { background-color: var(--ivory); }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
h1, h2, h3 { color: var(--green); letter-spacing: -0.02em; }
.hero { background: linear-gradient(135deg, #0F5C4D 0%, #0B6B57 100%); color: white; padding: 28px 32px; border-radius: 24px; box-shadow: var(--shadow); margin-bottom: 1.5rem; }
.hero-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 0.25rem; }
.hero-subtitle { font-size: 1rem; color: rgba(255,255,255,0.88); margin-bottom: 0.4rem; }
.hero-tag { display: inline-block; margin-top: 0.5rem; background: rgba(201,162,39,0.18); color: #F6E7B7; border: 1px solid rgba(201,162,39,0.35); padding: 8px 12px; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }
.card { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 22px; box-shadow: var(--shadow); margin-bottom: 1rem; }
.card-title { color: var(--green); font-size: 1.05rem; font-weight: 700; margin-bottom: 0.9rem; }
.muted { color: var(--muted); font-size: 0.95rem; }
.badge { display: inline-block; padding: 6px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 700; margin-right: 8px; margin-bottom: 6px; }
.badge-green { background: rgba(15,92,77,0.10); color: var(--green); border: 1px solid rgba(15,92,77,0.18); }
.badge-gold { background: rgba(201,162,39,0.14); color: #8A6B00; border: 1px solid rgba(201,162,39,0.25); }
.metric-row { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 10px; }
.metric-box { flex: 1; min-width: 180px; background: linear-gradient(180deg, #FFFFFF 0%, #FCFCFA 100%); border: 1px solid var(--border); border-radius: 16px; padding: 16px; }
.metric-label { font-size: 0.85rem; color: var(--muted); margin-bottom: 6px; }
.metric-value { font-size: 1.8rem; font-weight: 800; color: var(--green); line-height: 1.1; }
.metric-sub { margin-top: 6px; color: var(--muted); font-size: 0.85rem; }
.vs-line { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 10px 0 6px 0; }
.team-name { font-size: 1.3rem; font-weight: 800; color: var(--green); }
.team-rank { color: var(--muted); font-size: 0.9rem; }
.vs-center { font-size: 1rem; font-weight: 800; color: var(--gold); padding: 8px 12px; border-radius: 999px; background: rgba(201,162,39,0.12); border: 1px solid rgba(201,162,39,0.25); }
.prob-wrap { margin-top: 8px; }
.prob-label-row { display: flex; justify-content: space-between; font-size: 0.92rem; margin-bottom: 6px; color: var(--text); font-weight: 600; }
.prob-track { width: 100%; height: 12px; background: #ECEBE5; border-radius: 999px; overflow: hidden; margin-bottom: 14px; }
.prob-fill-green { height: 100%; background: linear-gradient(90deg, #0F5C4D, #16806A); border-radius: 999px; }
.prob-fill-gold { height: 100%; background: linear-gradient(90deg, #C9A227, #E1C15B); border-radius: 999px; }
.prob-fill-gray { height: 100%; background: linear-gradient(90deg, #6B7280, #8B93A1); border-radius: 999px; }
.score-pill { display: inline-block; padding: 10px 14px; margin: 6px 8px 0 0; border-radius: 12px; background: #FAFAF7; border: 1px solid var(--border); font-weight: 700; color: var(--green); }
.insight { border-left: 4px solid var(--gold); background: #FFFDF6; padding: 14px 16px; border-radius: 12px; color: var(--text); line-height: 1.5; }
.stButton > button { width: 100%; background: linear-gradient(135deg, #0F5C4D 0%, #0B6B57 100%); color: white; border: none; border-radius: 12px; padding: 0.7rem 1rem; font-weight: 700; box-shadow: 0 4px 14px rgba(15,92,77,0.18); }
.stButton > button:hover { background: linear-gradient(135deg, #0B6B57 0%, #095645 100%); color: white; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 12px 12px 0 0; padding: 10px 20px; font-weight: 600; }
.stTabs [aria-selected="true"] { background-color: #0F5C4D !important; color: white !important; }
hr { border: none; border-top: 1px solid rgba(15,92,77,0.08); margin: 1.2rem 0; }
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


def build_match_insight(result, team_a, team_b):
    a = result["team_a_win"]
    d = result["draw"]
    b = result["team_b_win"]
    la = result["team_a_lambda"]
    lb = result["team_b_lambda"]
    mt = result.get("match_type", "Competitive")
    if abs(a - b) <= 6:
        edge = team_a + " and " + team_b + " project as closely matched."
    elif a > b:
        edge = team_a + " enter as the more likely winner."
    else:
        edge = team_b + " look slightly stronger in the current model."
    if d >= 27:
        dr = "Draw probability is elevated, pointing to a compact match."
    elif d <= 20:
        dr = "Draw probability is modest, suggesting a decisive result."
    else:
        dr = "A draw remains a meaningful live outcome."
    if la + lb >= 2.9:
        gl = "Expected goals indicate a potentially open game."
    elif la + lb <= 2.3:
        gl = "Expected goals suggest a lower-scoring contest."
    else:
        gl = "Expected goals point to a moderate scoring environment."
    return mt + ". " + edge + " " + dr + " " + gl


teams = get_team_list()

st.markdown('''
<div class="hero">
    <div class="hero-title">Mundialista AI</div>
    <div class="hero-subtitle">International Match Intelligence</div>
    <div class="hero-tag">Refined match predictions - Global national teams - Visual-first analytics</div>
</div>
''', unsafe_allow_html=True)

st.markdown('<div class="card"><div class="card-title">Match Setup</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="card">', unsafe_allow_html=True)
    v = '<div class="vs-line"><div><div class="team-name">' + da + '</div>'
    v += '<div class="team-rank">FIFA Rank: ' + str(rk_a) + '</div></div>'
    v += '<div class="vs-center">VS</div>'
    v += '<div style="text-align:right;"><div class="team-name">' + db + '</div>'
    v += '<div class="team-rank">FIFA Rank: ' + str(rk_b) + '</div></div></div>'
    st.markdown(v, unsafe_allow_html=True)

    vl = "Neutral Venue" if neutral else "Home Advantage Active"
    st.markdown(badge_html(mt, "gold") + badge_html(vl, "green"), unsafe_allow_html=True)

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

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">Win / Draw / Loss Profile</div>', unsafe_allow_html=True)
    p = '<div class="prob-wrap">'
    p += '<div class="prob-label-row"><span>' + da + ' win</span><span>' + wa + '%</span></div>'
    p += '<div class="prob-track"><div class="prob-fill-green" style="width:' + wa + '%;"></div></div>'
    p += '<div class="prob-label-row"><span>Draw</span><span>' + dv + '%</span></div>'
    p += '<div class="prob-track"><div class="prob-fill-gold" style="width:' + dv + '%;"></div></div>'
    p += '<div class="prob-label-row"><span>' + db + ' win</span><span>' + wb + '%</span></div>'
    p += '<div class="prob-track"><div class="prob-fill-gray" style="width:' + wb + '%;"></div></div></div>'
    st.markdown(p, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    s1, s2 = st.columns([1, 1])
    with s1:
        st.markdown('<div class="card-title">Expected Goals</div>', unsafe_allow_html=True)
        x = '<div class="metric-row">'
        x += '<div class="metric-box"><div class="metric-label">' + da + '</div>'
        x += '<div class="metric-value">' + la_s + '</div>'
        x += '<div class="metric-sub">Expected goals</div></div>'
        x += '<div class="metric-box"><div class="metric-label">' + db + '</div>'
        x += '<div class="metric-value">' + lb_s + '</div>'
        x += '<div class="metric-sub">Expected goals</div></div></div>'
        st.markdown(x, unsafe_allow_html=True)
    with s2:
        st.markdown('<div class="card-title">Most Likely Scorelines</div>', unsafe_allow_html=True)
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

    st.markdown("<hr>", unsafe_allow_html=True)
    ins = build_match_insight(result, da, db)
    st.markdown('<div class="card-title">Model Insight</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight">' + ins + '</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Visual Analytics</div>', unsafe_allow_html=True)
    t1, t2, t3, t4, t5 = st.tabs(["Summary Card", "Win Probability", "Score Matrix", "Top Scorelines", "Goal Distribution"])
    with t1:
        if "summary" in charts and os.path.exists(charts["summary"]):
            st.image(charts["summary"], use_container_width=True)
        else:
            st.info("Summary chart not available.")
    with t2:
        if "probability" in charts and os.path.exists(charts["probability"]):
            st.image(charts["probability"], use_container_width=True)
        else:
            st.info("Probability chart not available.")
    with t3:
        if "matrix" in charts and os.path.exists(charts["matrix"]):
            st.image(charts["matrix"], use_container_width=True)
        else:
            st.info("Score matrix not available.")
    with t4:
        if "top_scores" in charts and os.path.exists(charts["top_scores"]):
            st.image(charts["top_scores"], use_container_width=True)
        else:
            st.info("Top scores chart not available.")
    with t5:
        if "goals" in charts and os.path.exists(charts["goals"]):
            st.image(charts["goals"], use_container_width=True)
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
    <div class="card">
        <div class="card-title">How to use</div>
        <div class="muted">
            Select two national teams, choose whether the match is on neutral ground, and click
            <strong>Generate Prediction</strong> to view win probabilities, expected goals, likely scorelines,
            model-generated match insight, and full visual analytics charts.
        </div>
    </div>
    ''', unsafe_allow_html=True)
