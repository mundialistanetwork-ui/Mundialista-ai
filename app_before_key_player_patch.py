
"""
Mundialista AI — Streamlit Web Interface v2.1
Fixed: cloud-safe paths, merged H2H, knockout mode, improved card simulation
"""

import matplotlib
matplotlib.use("Agg")

import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from prediction_engine import predict, get_all_teams, get_team_ranking
from chart_generator import generate_all_charts

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

st.set_page_config(
    page_title="Mundialista AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.03); }
}
html, body, [class*="css"] {
    font-family: Impact, 'Arial Black', 'Trebuchet MS', sans-serif;
}
.main {
    background: linear-gradient(180deg, #0a0a2e, #1a0a3e, #0a1a2e);
    color: #e0e0ff;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
.hero {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
}
.hero-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00f0ff, #ffd700, #ff00aa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #8888cc;
    letter-spacing: 2px;
    margin-top: 4px;
}
.hero-tag {
    font-size: 0.85rem;
    color: #666688;
    margin-top: 8px;
    font-family: 'Trebuchet MS', sans-serif;
}
.retro-card {
    background: linear-gradient(180deg, #141430, #1a1a40);
    border: 2px solid #00f0ff;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 1rem;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
}
.retro-card-pink  { border-color: #ff00aa; box-shadow: 0 0 15px rgba(255,0,170,0.15); }
.retro-card-green { border-color: #00ff88; box-shadow: 0 0 15px rgba(0,255,136,0.15); }
.retro-card-gold  { border-color: #ffd700; box-shadow: 0 0 15px rgba(255,215,0,0.15); }
.retro-card-title {
    font-size: 1.2rem;
    font-weight: 900;
    color: #ffd700;
    text-shadow: 1px 1px 0 #ff6600;
    margin-bottom: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.vs-line {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
}
.team-name {
    font-size: 1.5rem;
    font-weight: 900;
    color: #00f0ff;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
}
.team-rank {
    color: #8888aa;
    font-size: 0.85rem;
    font-family: "Courier New", monospace;
}
.vs-center {
    font-size: 1.4rem;
    font-weight: 900;
    color: #ffd700;
    text-shadow: 2px 2px 0 #ff6600;
    padding: 8px 16px;
    border: 2px solid #ffd700;
    border-radius: 50%;
    background: rgba(255, 215, 0, 0.1);
    animation: pulse 2s ease-in-out infinite;
}
.match-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 900;
    margin: 6px 8px 6px 0;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-elite      { background: linear-gradient(90deg,#ff6600,#ff0033); color: white; border: 2px solid #ff0033; animation: pulse 2s ease-in-out infinite; }
.badge-mismatch   { background: linear-gradient(90deg,#8b0000,#4a0000); color: #ff6666; border: 2px solid #ff3333; }
.badge-favorite   { background: linear-gradient(90deg,#004e92,#0066cc); color: #88ccff; border: 2px solid #00aaff; }
.badge-competitive{ background: linear-gradient(90deg,#006644,#00aa66); color: #88ffcc; border: 2px solid #00ff88; }
.badge-showdown   { background: linear-gradient(90deg,#660066,#aa00aa); color: #ff88ff; border: 2px solid #ff00ff; }
.badge-venue      { background: rgba(255,215,0,0.15); color: #ffd700; border: 2px solid #ffd700; }
.badge-knockout   { background: linear-gradient(90deg,#4b0082,#8a2be2); color: #f3d9ff; border: 2px solid #d78cff; }
.metric-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin: 12px 0;
}
.metric-box {
    flex: 1;
    min-width: 140px;
    background: linear-gradient(180deg, #1a1a40, #0a0a2e);
    border: 2px solid #00f0ff;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}
.metric-label {
    font-size: 0.8rem;
    color: #8888cc;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 900;
    color: #00f0ff;
    text-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
}
.metric-value-gold { color: #ffd700; text-shadow: 0 0 15px rgba(255,215,0,0.5); }
.metric-value-pink { color: #ff00aa; text-shadow: 0 0 15px rgba(255,0,170,0.5); }
.metric-sub {
    font-size: 0.7rem;
    color: #666688;
    margin-top: 4px;
}
.prob-wrap { margin: 8px 0; }
.prob-label-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    color: #ccccff;
    margin-bottom: 4px;
    font-weight: 700;
}
.prob-track {
    width: 100%;
    height: 18px;
    background: #0a0a2e;
    border-radius: 10px;
    border: 1px solid #333366;
    overflow: hidden;
    margin-bottom: 10px;
}
.prob-fill-cyan { height:100%; background:linear-gradient(90deg,#004466,#00f0ff); border-radius:10px; box-shadow:0 0 10px rgba(0,240,255,0.4); }
.prob-fill-gold { height:100%; background:linear-gradient(90deg,#665500,#ffd700); border-radius:10px; box-shadow:0 0 10px rgba(255,215,0,0.4); }
.prob-fill-pink { height:100%; background:linear-gradient(90deg,#660044,#ff00aa); border-radius:10px; box-shadow:0 0 10px rgba(255,0,170,0.4); }
.score-pill {
    display: inline-block;
    padding: 10px 16px;
    margin: 5px;
    border-radius: 12px;
    background: linear-gradient(180deg, #1a1a40, #0a0a2e);
    border: 2px solid #00f0ff;
    font-weight: 900;
    font-size: 1.0rem;
    color: #00f0ff;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
}
.score-pill-top {
    border-color: #ffd700;
    color: #ffd700;
    text-shadow: 0 0 8px rgba(255, 215, 0, 0.4);
    font-size: 1.2rem;
    animation: pulse 2s ease-in-out infinite;
}
.star-player {
    display: inline-block;
    padding: 6px 12px;
    margin: 4px;
    border-radius: 10px;
    background: linear-gradient(90deg, #1a1a40, #2a1a50);
    border: 1px solid #ffd700;
    color: #ffd700;
    font-size: 0.85rem;
    font-weight: 700;
}
.h2h-bar {
    display: flex;
    height: 30px;
    border-radius: 8px;
    overflow: hidden;
    margin: 10px 0;
    border: 1px solid #333366;
}
.h2h-win  { background: #00f0ff; }
.h2h-draw { background: #ffd700; }
.h2h-loss { background: #ff00aa; }
.insight-retro {
    border-left: 4px solid #ffd700;
    background: linear-gradient(90deg, rgba(255,215,0,0.05), transparent);
    padding: 14px 18px;
    border-radius: 0 12px 12px 0;
    color: #ccccff;
    line-height: 1.6;
    font-family: 'Trebuchet MS', sans-serif;
}
.retro-divider {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00f0ff, #ffd700, #ff00aa, transparent);
    margin: 1.2rem 0;
}
.muted {
    color: #666688;
    font-family: 'Trebuchet MS', sans-serif;
    line-height: 1.6;
}
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #ff6600, #ff0033);
    color: white;
    border: 2px solid #ffd700;
    border-radius: 14px;
    padding: 0.8rem 1rem;
    font-weight: 900;
    font-size: 1rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    box-shadow: 0 0 20px rgba(255, 102, 0, 0.3);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #ff0033, #cc0066);
    border-color: #00f0ff;
}
.stSelectbox label { color: #00f0ff !important; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.stCheckbox label  { color: #ffd700 !important; font-weight: 700; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 12px 12px 0 0;
    padding: 10px 16px;
    font-weight: 700;
    color: #8888cc;
    background: #141430;
    border: 1px solid #333366;
}
.stTabs [aria-selected="true"] {
    background: #00f0ff !important;
    color: #0a0a2e !important;
    border-color: #00f0ff !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_team_list():
    try:
        rankings = pd.read_csv(DATA_DIR / "rankings.csv")
        if "country_full" in rankings.columns:
            return sorted(rankings["country_full"].dropna().unique().tolist())
    except FileNotFoundError:
        pass
    return get_all_teams()

def load_results_merged():
    frames = []
    for path in [DATA_DIR / "results.csv", DATA_DIR / "recent_results.csv"]:
        if path.exists():
            try:
                df = pd.read_csv(path)
                if not df.empty:
                    frames.append(df)
            except Exception:
                pass
    if not frames:
        return pd.DataFrame(columns=["date","home_team","away_team","home_score","away_score","tournament","neutral"])
    df = pd.concat(frames, ignore_index=True, sort=False)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.sort_values("date", ascending=False)

def compute_h2h(team_a, team_b, max_matches=20):
    df = load_results_merged()
    if df.empty:
        return {"matches": 0}
    mask = (
        ((df["home_team"] == team_a) & (df["away_team"] == team_b)) |
        ((df["home_team"] == team_b) & (df["away_team"] == team_a))
    )
    h2h = df[mask].head(max_matches)
    if h2h.empty:
        return {"matches": 0}

    wins_a = wins_b = draws = 0
    recent = []

    for _, row in h2h.iterrows():
        hs_raw = row.get("home_score", 0)
        aws_raw = row.get("away_score", 0)

        hs = 0 if pd.isna(hs_raw) else int(hs_raw)
        aws = 0 if pd.isna(aws_raw) else int(aws_raw)

        ht = row.get("home_team", "")
        at = row.get("away_team", "")

        if hs > aws:
            winner = ht
        elif aws > hs:
            winner = at
        else:
            winner = None

        if winner == team_a:
            wins_a += 1
        elif winner == team_b:
            wins_b += 1
        else:
            draws += 1

        if len(recent) < 5:
            recent.append({
                "date": str(row.get("date", ""))[:10],
                "home": ht,
                "away": at,
                "score": f"{hs}-{aws}",
                "tournament": row.get("tournament", ""),
            })

    return {
        "matches": len(h2h),
        "wins_a": wins_a,
        "wins_b": wins_b,
        "draws": draws,
        "recent": recent,
    }

def safe_json(result):
    clean = {}
    for k, v in result.items():
        if isinstance(v, np.ndarray):
            clean[k] = f"[array shape={v.shape}]"
        elif isinstance(v, (np.integer,)):
            clean[k] = int(v)
        elif isinstance(v, (np.floating,)):
            clean[k] = float(v)
        else:
            clean[k] = v
    return clean

def poisson_pmf(k, lam):
    if lam < 0:
        lam = 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def et_outcome_probs(lambda_a, lambda_b, max_goals=10, et_scale=0.28):
    la = max(0.0, lambda_a * et_scale)
    lb = max(0.0, lambda_b * et_scale)
    a_win = draw = b_win = 0.0
    for ga in range(max_goals + 1):
        pga = poisson_pmf(ga, la)
        for gb in range(max_goals + 1):
            p = pga * poisson_pmf(gb, lb)
            if ga > gb:
                a_win += p
            elif ga < gb:
                b_win += p
            else:
                draw += p
    total = a_win + draw + b_win
    if total > 0:
        a_win /= total
        draw /= total
        b_win /= total
    return {
        "a_win_et_cond": a_win,
        "draw_et_cond": draw,
        "b_win_et_cond": b_win,
        "lambda_a_et": la,
        "lambda_b_et": lb,
    }

def penalty_shootout_probs(team_a, team_b, result):
    rank_a = float(result.get("team_a_rank", 100))
    rank_b = float(result.get("team_b_rank", 100))
    rank_edge = (rank_b - rank_a) / 100.0
    boost_a = float(result.get("team_a_star_boost", 1.0))
    boost_b = float(result.get("team_b_star_boost", 1.0))
    def_a = float(result.get("team_a_def_boost", 1.0))
    def_b = float(result.get("team_b_def_boost", 1.0))
    star_edge = (boost_a - boost_b) * 0.25
    keeper_edge = (def_a - def_b) * 0.20
    p_a = 0.50 + 0.12 * rank_edge + star_edge + keeper_edge
    p_a = float(np.clip(p_a, 0.40, 0.60))
    return {"a_pen_win_cond": p_a, "b_pen_win_cond": 1.0 - p_a}

def simulate_knockout(team_a, team_b, result):
    a90 = float(result.get("team_a_win", 0.0)) / 100.0
    d90 = float(result.get("draw", 0.0)) / 100.0
    b90 = float(result.get("team_b_win", 0.0)) / 100.0
    la = float(result.get("team_a_lambda", 0.0))
    lb = float(result.get("team_b_lambda", 0.0))

    et = et_outcome_probs(la, lb)
    pens = penalty_shootout_probs(team_a, team_b, result)

    a_win_90 = a90
    b_win_90 = b90
    a_win_et = d90 * et["a_win_et_cond"]
    b_win_et = d90 * et["b_win_et_cond"]
    a_win_pens = d90 * et["draw_et_cond"] * pens["a_pen_win_cond"]
    b_win_pens = d90 * et["draw_et_cond"] * pens["b_pen_win_cond"]

    return {
        "team_a_advance": round((a_win_90 + a_win_et + a_win_pens) * 100, 1),
        "team_b_advance": round((b_win_90 + b_win_et + b_win_pens) * 100, 1),
        "team_a_win_90": round(a_win_90 * 100, 1),
        "team_b_win_90": round(b_win_90 * 100, 1),
        "team_a_win_et": round(a_win_et * 100, 1),
        "team_b_win_et": round(b_win_et * 100, 1),
        "team_a_win_pens": round(a_win_pens * 100, 1),
        "team_b_win_pens": round(b_win_pens * 100, 1),
        "draw_after_90": round(d90 * 100, 1),
        "team_a_et_lambda": round(et["lambda_a_et"], 3),
        "team_b_et_lambda": round(et["lambda_b_et"], 3),
    }

def compute_card_risk(team_a, team_b, result, knockout=False):
    a_win = float(result.get("team_a_win", 33.3))
    b_win = float(result.get("team_b_win", 33.3))
    draw = float(result.get("draw", 33.4))
    closeness = 1.0 - min(abs(a_win - b_win) / 100.0, 1.0)
    draw_factor = draw / 100.0
    xg_total = float(result.get("team_a_lambda", 1.2)) + float(result.get("team_b_lambda", 1.1))

def build_simple_insight(result, team_a, team_b, knockout=False, ko_data=None):
    a = float(result.get("team_a_win", 0.0))
    b = float(result.get("team_b_win", 0.0))
    d = float(result.get("draw", 0.0))
    la = float(result.get("team_a_lambda", 0.0))
    lb = float(result.get("team_b_lambda", 0.0))

    lines = []

    if abs(a - b) <= 6:
        lines.append(f"🤜🤛 {team_a} and {team_b} look closely matched.")
    elif a > b:
        lines.append(f"📈 {team_a} hold the edge on the 90-minute model.")
    else:
        lines.append(f"📈 {team_b} hold the edge on the 90-minute model.")

    total_xg = la + lb
    if total_xg >= 3.0:
        lines.append(f"🔥 The model expects a relatively open game ({total_xg:.1f} total xG).")
    elif total_xg <= 2.2:
        lines.append(f"🔒 This projects as a tighter tactical contest ({total_xg:.1f} total xG).")
    else:
        lines.append(f"⚽ Expect a balanced scoring profile ({total_xg:.1f} total xG).")

    if d >= 27:
        lines.append("🤝 Draw risk is meaningful after 90 minutes.")

    if knockout and ko_data:
        draw90 = float(ko_data.get("draw_after_90", 0.0))
        pens = float(ko_data.get("team_a_win_pens", 0.0)) + float(ko_data.get("team_b_win_pens", 0.0))
        if draw90 >= 28:
            lines.append("⏳ Extra time is a realistic path here.")
        if pens >= 10:
            lines.append("🎯 Penalties are a meaningful possibility.")

    return " ".join(lines)


    heat_index = 4.8 + 2.0 * closeness + 1.0 * draw_factor
    if knockout:
        heat_index += 0.9
    if xg_total < 2.3:
        heat_index += 0.4
    elif xg_total > 3.2:
        heat_index -= 0.2
    heat_index = float(np.clip(heat_index, 1.0, 10.0))

    total_yellows = 2.6 + 0.38 * heat_index
    red_prob = float(np.clip(0.05 + 0.025 * max(0.0, heat_index - 4.0), 0.05, 0.30))

    da = float(result.get("team_a_def_boost", 1.0))
    db = float(result.get("team_b_def_boost", 1.0))
    split_a = float(np.clip(0.5 + (da - db) * 0.08, 0.40, 0.60))
    split_b = 1.0 - split_a

    if red_prob >= 0.22:
        risk_label = "High"
    elif red_prob >= 0.14:
        risk_label = "Moderate"
    else:
        risk_label = "Low"

    return {
        "heat_index": round(heat_index, 1),
        "yellows_a": round(total_yellows * split_a, 1),
        "yellows_b": round(total_yellows * split_b, 1),
        "total_yellows": round(total_yellows, 1),
        "red_prob": round(red_prob * 100, 1),
        "risk_label": risk_label,
    }

st.title("⚽ Mundialista AI")
st.caption("World Cup 2026 Match Intelligence")

teams = get_team_list()
if not teams:
    st.error("No team data found. Run python get_data.py first.")
    st.stop()

col1, col2, col3 = st.columns([1,1,1])
with col1:
    idx_a = teams.index("Argentina") if "Argentina" in teams else 0
    team_a = st.selectbox("Home / Team A", teams, index=idx_a)
with col2:
    idx_b = teams.index("Brazil") if "Brazil" in teams else min(1, len(teams)-1)
    team_b = st.selectbox("Away / Team B", teams, index=idx_b)
with col3:
    neutral = st.checkbox("Neutral venue", value=True)
    knockout = st.checkbox("Knockout match", value=False)

run_prediction = st.button("⚽ Generate Prediction")

if run_prediction:
    if team_a == team_b:
        st.warning("Choose two different teams.")
    else:
        home = None if neutral else team_a
        result = predict(team_a, team_b, home=home)
        charts = generate_all_charts(result, team_a, team_b)
        h2h = compute_h2h(team_a, team_b)
        ko_data = simulate_knockout(team_a, team_b, result) if knockout else None
        card_data = compute_card_risk(team_a, team_b, result, knockout=knockout)

        st.session_state["result"] = result
        st.session_state["charts"] = charts
        st.session_state["h2h"] = h2h
        st.session_state["ko_data"] = ko_data
        st.session_state["card_data"] = card_data
        st.session_state["pred_a"] = team_a
        st.session_state["pred_b"] = team_b
        st.session_state["neutral"] = neutral
        st.session_state["knockout"] = knockout

if "result" in st.session_state:
    result = st.session_state["result"]
    charts = st.session_state.get("charts", {})
    h2h = st.session_state.get("h2h", {"matches": 0})
    ko_data = st.session_state.get("ko_data")
    card_data = st.session_state.get("card_data")
    da = st.session_state["pred_a"]
    db = st.session_state["pred_b"]
    is_neutral = st.session_state.get("neutral", True)
    is_knockout = st.session_state.get("knockout", False)

    wa = float(result.get("team_a_win", 0.0))
    dr = float(result.get("draw", 0.0))
    wb = float(result.get("team_b_win", 0.0))
    xga = float(result.get("team_a_lambda", 0.0))
    xgb = float(result.get("team_b_lambda", 0.0))
    rk_a = result.get("team_a_rank", "N/A")
    rk_b = result.get("team_b_rank", "N/A")
    match_type = result.get("match_type", "Match")
    top_scores = result.get("top_scores", [])[:5]

    st.markdown(f"## {da} vs {db}")
    st.caption(f"FIFA Rank #{rk_a} vs FIFA Rank #{rk_b}")

    badge_parts = [f"**{match_type}**"]
    badge_parts.append("🏟️ Neutral Venue" if is_neutral else "🏠 Home Advantage Active")
    if is_knockout:
        badge_parts.append("🏆 Knockout Mode")
    st.markdown(" • ".join(badge_parts))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(f"{da} Win", f"{wa:.1f}%")
    with c2:
        st.metric("Draw", f"{dr:.1f}%")
    with c3:
        st.metric(f"{db} Win", f"{wb:.1f}%")

    st.markdown("### ⚽ Expected Goals")
    gx1, gx2 = st.columns(2)
    with gx1:
        st.metric(f"{da} xG", f"{xga:.2f}")
    with gx2:
        st.metric(f"{db} xG", f"{xgb:.2f}")

    stars_a = result.get("team_a_stars", [])
    stars_b = result.get("team_b_stars", [])
    boost_a = float(result.get("team_a_star_boost", 1.0))
    boost_b = float(result.get("team_b_star_boost", 1.0))
    def_a = float(result.get("team_a_def_boost", 1.0))
    def_b = float(result.get("team_b_def_boost", 1.0))

    st.markdown("### 🌟 Star Player Impact")
    sa, sb = st.columns(2)
    with sa:
        st.markdown(f"**{da}** — ATK x{boost_a:.2f} | DEF x{def_a:.2f}")
        if stars_a:
            for p in stars_a[:5]:
                st.markdown(f"- {p}")
        else:
            st.caption("No star player data")
    with sb:
        st.markdown(f"**{db}** — ATK x{boost_b:.2f} | DEF x{def_b:.2f}")
        if stars_b:
            for p in stars_b[:5]:
                st.markdown(f"- {p}")
        else:
            st.caption("No star player data")

    if top_scores:
        st.markdown("### 🎯 Most Likely Scorelines")
        score_cols = st.columns(min(5, len(top_scores)))
        for i, sc in enumerate(top_scores):
            with score_cols[i]:
                if isinstance(sc, (list, tuple)) and len(sc) >= 2:
                    scoreline = str(sc[0])
                    pct = sc[1]
                    if isinstance(pct, float) and pct < 1:
                        label = f"{pct*100:.1f}%"
                    elif isinstance(pct, float):
                        label = f"{pct:.1f}%"
                    else:
                        label = ""
                    st.metric(scoreline, label)
                else:
                    st.write(sc)

    if is_knockout and ko_data:
        st.markdown("### 🏆 Knockout Advancement Paths")
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric(f"{da} Advance", f"{ko_data.get('team_a_advance', 0):.1f}%")
            st.metric(f"{da} Win in 90", f"{ko_data.get('team_a_win_90', 0):.1f}%")
            st.metric(f"{da} Win in ET", f"{ko_data.get('team_a_win_et', 0):.1f}%")
            st.metric(f"{da} Win on Pens", f"{ko_data.get('team_a_win_pens', 0):.1f}%")
        with k2:
            st.metric("Level after 90", f"{ko_data.get('draw_after_90', 0):.1f}%")
            st.metric(f"{da} ET xG", f"{ko_data.get('team_a_et_lambda', 0):.3f}")
            st.metric(f"{db} ET xG", f"{ko_data.get('team_b_et_lambda', 0):.3f}")
        with k3:
            st.metric(f"{db} Advance", f"{ko_data.get('team_b_advance', 0):.1f}%")
            st.metric(f"{db} Win in 90", f"{ko_data.get('team_b_win_90', 0):.1f}%")
            st.metric(f"{db} Win in ET", f"{ko_data.get('team_b_win_et', 0):.1f}%")
            st.metric(f"{db} Win on Pens", f"{ko_data.get('team_b_win_pens', 0):.1f}%")

    st.markdown("### ⚔️ Head-to-Head")
    if h2h.get("matches", 0) == 0:
        st.info("No previous meetings found in database.")
    else:
        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.metric(f"{da} Wins", h2h.get("wins_a", 0))
        with hc2:
            st.metric("Draws", h2h.get("draws", 0))
        with hc3:
            st.metric(f"{db} Wins", h2h.get("wins_b", 0))

        recent = h2h.get("recent", [])
        if recent:
            st.markdown("**Recent meetings**")
            for m in recent:
                st.markdown(
                    f"- {m.get('date','')} — **{m.get('home','')} {m.get('score','')} {m.get('away','')}** "
                    f"*[{m.get('tournament','')}]*"
                )

    if card_data:
        st.markdown("### 🟥 Discipline Risk")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.metric("Heat Index", f"{card_data.get('heat_index', 0):.1f}/10")
        with d2:
            st.metric("Expected Yellows", f"{card_data.get('total_yellows', 0):.1f}")
            st.caption(f"{da}: {card_data.get('yellows_a', 0):.1f} • {db}: {card_data.get('yellows_b', 0):.1f}")
        with d3:
            st.metric("Red Card Risk", f"{card_data.get('red_prob', 0):.1f}%")
            st.caption(f"{card_data.get('risk_label', 'Unknown')} risk")

    st.markdown("### 🧠 Match Insight")
    st.info(build_simple_insight(result, da, db, knockout=is_knockout, ko_data=ko_data))

    if charts:
        st.markdown("### 📈 Visual Analytics")
        tabs = st.tabs(["Summary", "Probability", "Matrix", "Top Scores", "Goals"])
        chart_keys = ["summary", "probability", "matrix", "top_scores", "goals"]

        for tab, key in zip(tabs, chart_keys):
            with tab:
                chart_path = charts.get(key, "")
                if chart_path and Path(chart_path).exists():
                    st.image(str(chart_path), use_container_width=True)
                else:
                    st.caption(f"{key} chart not available.")

    with st.expander("🔧 Raw Prediction Output"):
        payload = safe_json(result).copy()
        if ko_data:
            payload["knockout"] = ko_data
        if card_data:
            payload["discipline"] = card_data
        st.json(payload)
