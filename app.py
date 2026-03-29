import streamlit as st
import pandas as pd
from prediction_engine import predict, load_rankings

st.set_page_config(
    page_title="Mundialista AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown('''
<style>
:root {
    --green: #0F5C4D;
    --green-2: #0B6B57;
    --gold: #C9A227;
    --gold-soft: #E9D48A;
    --ivory: #F8F7F2;
    --white: #FFFFFF;
    --text: #1E1E1E;
    --muted: #6B7280;
    --border: rgba(15, 92, 77, 0.12);
    --shadow: 0 6px 22px rgba(0, 0, 0, 0.05);
    --radius: 18px;
}

html, body, [class*="css"] {
    font-family: "Segoe UI", "Inter", sans-serif;
}

.main {
    background-color: var(--ivory);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

h1, h2, h3 {
    color: var(--green);
    letter-spacing: -0.02em;
}

.hero {
    background: linear-gradient(135deg, #0F5C4D 0%, #0B6B57 100%);
    color: white;
    padding: 28px 32px;
    border-radius: 24px;
    box-shadow: var(--shadow);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.08);
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 0.25rem;
}

.hero-subtitle {
    font-size: 1rem;
    color: rgba(255,255,255,0.88);
    margin-bottom: 0.4rem;
}

.hero-tag {
    display: inline-block;
    margin-top: 0.5rem;
    background: rgba(201, 162, 39, 0.18);
    color: #F6E7B7;
    border: 1px solid rgba(201, 162, 39, 0.35);
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
}

.card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 22px;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}

.card-title {
    color: var(--green);
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.9rem;
}

.muted {
    color: var(--muted);
    font-size: 0.95rem;
}

.badge {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-right: 8px;
    margin-bottom: 6px;
}

.badge-green {
    background: rgba(15, 92, 77, 0.10);
    color: var(--green);
    border: 1px solid rgba(15, 92, 77, 0.18);
}

.badge-gold {
    background: rgba(201, 162, 39, 0.14);
    color: #8A6B00;
    border: 1px solid rgba(201, 162, 39, 0.25);
}

.badge-gray {
    background: rgba(107, 114, 128, 0.10);
    color: #4B5563;
    border: 1px solid rgba(107, 114, 128, 0.18);
}

.metric-row {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin-top: 10px;
}

.metric-box {
    flex: 1;
    min-width: 180px;
    background: linear-gradient(180deg, #FFFFFF 0%, #FCFCFA 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
}

.metric-label {
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 6px;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--green);
    line-height: 1.1;
}

.metric-sub {
    margin-top: 6px;
    color: var(--muted);
    font-size: 0.85rem;
}

.vs-line {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 10px 0 6px 0;
}

.team-name {
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--green);
}

.team-rank {
    color: var(--muted);
    font-size: 0.9rem;
}

.vs-center {
    font-size: 1rem;
    font-weight: 800;
    color: var(--gold);
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(201, 162, 39, 0.12);
    border: 1px solid rgba(201, 162, 39, 0.25);
}

.prob-wrap {
    margin-top: 8px;
}

.prob-label-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.92rem;
    margin-bottom: 6px;
    color: var(--text);
    font-weight: 600;
}

.prob-track {
    width: 100%;
    height: 12px;
    background: #ECEBE5;
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 14px;
}

.prob-fill-green {
    height: 100%;
    background: linear-gradient(90deg, #0F5C4D, #16806A);
    border-radius: 999px;
}

.prob-fill-gold {
    height: 100%;
    background: linear-gradient(90deg, #C9A227, #E1C15B);
    border-radius: 999px;
}

.prob-fill-gray {
    height: 100%;
    background: linear-gradient(90deg, #6B7280, #8B93A1);
    border-radius: 999px;
}

.score-pill {
    display: inline-block;
    padding: 10px 14px;
    margin: 6px 8px 0 0;
    border-radius: 12px;
    background: #FAFAF7;
    border: 1px solid var(--border);
    font-weight: 700;
    color: var(--green);
}

.insight {
    border-left: 4px solid var(--gold);
    background: #FFFDF6;
    padding: 14px 16px;
    border-radius: 12px;
    color: var(--text);
    line-height: 1.5;
}

div[data-testid="stSelectbox"] > div {
    border-radius: 12px;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #0F5C4D 0%, #0B6B57 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 1rem;
    font-weight: 700;
    box-shadow: 0 4px 14px rgba(15,92,77,0.18);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0B6B57 0%, #095645 100%);
    color: white;
}

hr {
    border: none;
    border-top: 1px solid rgba(15,92,77,0.08);
    margin: 1.2rem 0;
}
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
    klass = {
        "green": "badge badge-green",
        "gold": "badge badge-gold",
        "gray": "badge badge-gray"
    }.get(kind, "badge badge-green")
    return '<span class="' + klass + '">' + text + '</span>'


def build_match_insight(result, team_a, team_b):
    a = result["team_a_win"]
    d = result["draw"]
    b = result["team_b_win"]
    la = result["team_a_lambda"]
    lb = result["team_b_lambda"]
    match_type = result.get("match_type", "Competitive")

    if abs(a - b) <= 6:
        edge_text = team_a + " and " + team_b + " project as closely matched with only a narrow probability margin."
    elif a > b:
        edge_text = team_a + " enter as the more likely winner, though the edge is not overwhelming."
    else:
        edge_text = team_b + " look slightly stronger in the current model, but this remains competitive."

    if d >= 27:
        draw_text = "Draw probability is elevated, pointing to a compact match."
    elif d <= 20:
        draw_text = "Draw probability is modest, suggesting a decisive result is more likely."
    else:
        draw_text = "A draw remains a meaningful live outcome."

    if la + lb >= 2.9:
        goals_text = "Expected goals indicate a potentially open game."
    elif la + lb <= 2.3:
        goals_text = "Expected goals suggest a tighter, lower-scoring contest."
    else:
        goals_text = "Expected goals point to a moderate scoring environment."

    return match_type + ". " + edge_text + " " + draw_text + " " + goals_text


@st.cache_data
def cached_predict(team_a, team_b):
    return predict(team_a, team_b)


teams = get_team_list()

# Hero
st.markdown('''
<div class="hero">
    <div class="hero-title">Mundialista AI</div>
    <div class="hero-subtitle">International Match Intelligence</div>
    <div class="hero-subtitle">Probabilistic football forecasting powered by rankings, form, and Poisson simulation.</div>
    <div class="hero-tag">Refined match predictions - Global national teams - Visual-first analytics</div>
</div>
''', unsafe_allow_html=True)

# Match setup card
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

# Prediction
if run_prediction:
    if team_a == team_b:
        st.warning("Please choose two different teams.")
    else:
        try:
            result = cached_predict(team_a, team_b)

            rank_a = result.get("team_a_rank", "N/A")
            rank_b = result.get("team_b_rank", "N/A")
            la = result.get("team_a_lambda", 0.0)
            lb = result.get("team_b_lambda", 0.0)
            match_type = result.get("match_type", "Competitive")
            top_scores = result.get("top_scores", [])[:5]

            st.markdown('<div class="card">', unsafe_allow_html=True)

            vs_html = '<div class="vs-line">'
            vs_html += '<div><div class="team-name">' + team_a + '</div>'
            vs_html += '<div class="team-rank">FIFA Rank: ' + str(rank_a) + '</div></div>'
            vs_html += '<div class="vs-center">VS</div>'
            vs_html += '<div style="text-align:right;">'
            vs_html += '<div class="team-name">' + team_b + '</div>'
            vs_html += '<div class="team-rank">FIFA Rank: ' + str(rank_b) + '</div></div></div>'
            st.markdown(vs_html, unsafe_allow_html=True)

            venue_label = "Neutral Venue" if neutral else "Home Advantage Active"
            badge_row = badge_html(match_type, "gold") + badge_html(venue_label, "green")
            st.markdown(badge_row, unsafe_allow_html=True)

            metrics_html = '<div class="metric-row">'
            metrics_html += '<div class="metric-box"><div class="metric-label">' + team_a + ' Win</div>'
            metrics_html += '<div class="metric-value">' + f"{result['team_a_win']:.1f}" + '%</div>'
            metrics_html += '<div class="metric-sub">Model win probability</div></div>'
            metrics_html += '<div class="metric-box"><div class="metric-label">Draw</div>'
            metrics_html += '<div class="metric-value" style="color:#8A6B00;">' + f"{result['draw']:.1f}" + '%</div>'
            metrics_html += '<div class="metric-sub">Shared outcome probability</div></div>'
            metrics_html += '<div class="metric-box"><div class="metric-label">' + team_b + ' Win</div>'
            metrics_html += '<div class="metric-value">' + f"{result['team_b_win']:.1f}" + '%</div>'
            metrics_html += '<div class="metric-sub">Model win probability</div></div>'
            metrics_html += '</div>'
            st.markdown(metrics_html, unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            st.markdown('<div class="card-title">Win / Draw / Loss Profile</div>', unsafe_allow_html=True)

            prob_html = '<div class="prob-wrap">'
            prob_html += '<div class="prob-label-row"><span>' + team_a + ' win</span><span>' + f"{result['team_a_win']:.1f}" + '%</span></div>'
            prob_html += '<div class="prob-track"><div class="prob-fill-green" style="width:' + f"{result['team_a_win']}" + '%;"></div></div>'
            prob_html += '<div class="prob-label-row"><span>Draw</span><span>' + f"{result['draw']:.1f}" + '%</span></div>'
            prob_html += '<div class="prob-track"><div class="prob-fill-gold" style="width:' + f"{result['draw']}" + '%;"></div></div>'
            prob_html += '<div class="prob-label-row"><span>' + team_b + ' win</span><span>' + f"{result['team_b_win']:.1f}" + '%</span></div>'
            prob_html += '<div class="prob-track"><div class="prob-fill-gray" style="width:' + f"{result['team_b_win']}" + '%;"></div></div>'
            prob_html += '</div>'
            st.markdown(prob_html, unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            sub1, sub2 = st.columns([1, 1])

            with sub1:
                st.markdown('<div class="card-title">Expected Goals</div>', unsafe_allow_html=True)
                xg_html = '<div class="metric-row">'
                xg_html += '<div class="metric-box"><div class="metric-label">' + team_a + '</div>'
                xg_html += '<div class="metric-value">' + f"{la:.2f}" + '</div>'
                xg_html += '<div class="metric-sub">Expected goals</div></div>'
                xg_html += '<div class="metric-box"><div class="metric-label">' + team_b + '</div>'
                xg_html += '<div class="metric-value">' + f"{lb:.2f}" + '</div>'
                xg_html += '<div class="metric-sub">Expected goals</div></div>'
                xg_html += '</div>'
                st.markdown(xg_html, unsafe_allow_html=True)

            with sub2:
                st.markdown('<div class="card-title">Most Likely Scorelines</div>', unsafe_allow_html=True)
                if top_scores:
                    score_html = ""
                    for score in top_scores:
                        if isinstance(score, (list, tuple)) and len(score) >= 2:
                            score_html += '<span class="score-pill">' + str(score[0]) + ' - ' + str(score[1]) + '</span>'
                        else:
                            score_html += '<span class="score-pill">' + str(score) + '</span>'
                    st.markdown(score_html, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="muted">No scoreline breakdown available.</div>', unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            insight_text = build_match_insight(result, team_a, team_b)
            st.markdown('<div class="card-title">Model Insight</div>', unsafe_allow_html=True)
            st.markdown('<div class="insight">' + insight_text + '</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("Raw prediction output"):
                st.json(result)

        except Exception as e:
            st.error("Prediction failed: " + str(e))

else:
    st.markdown('''
    <div class="card">
        <div class="card-title">How to use</div>
        <div class="muted">
            Select two national teams, choose whether the match is on neutral ground, and click
            <strong>Generate Prediction</strong> to view win probabilities, expected goals, likely scorelines,
            and a model-generated match insight.
        </div>
    </div>
    ''', unsafe_allow_html=True)
