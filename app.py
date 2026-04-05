"""
Mundialista AI — Streamlit Web Interface v2
Fixed: home advantage, CSS, H2H, score display, numpy serialization
"""

import matplotlib
matplotlib.use("Agg")

import json
import numpy as np
import pandas as pd
import streamlit as st
# TEMPORARY DEBUG - REMOVE LATER
import os, pathlib
st.sidebar.write('CWD:', os.getcwd())
st.sidebar.write('rankings exists:', os.path.exists('data/rankings.csv'))
st.sidebar.write('data dir:', os.listdir('data') if os.path.exists('data') else 'NO DATA DIR')

from prediction_engine import predict, get_all_teams, get_team_ranking
from chart_generator import generate_all_charts

# ──────────────────────────────────────────────
#  PAGE CONFIG
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Mundialista AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
#  CSS (unified — every class used in HTML exists here)
# ──────────────────────────────────────────────

st.markdown("""
<style>
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.03); }
}

/* ── Base ── */
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

/* ── Hero ── */
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

/* ── Cards ── */
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

/* ── VS Header ── */
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

/* ── Match Badges ── */
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

/* ── Metrics ── */
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

/* ── Probability Bars ── */
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

/* ── Score Pills ── */
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

/* ── Star Players ── */
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

/* ── H2H Bar ── */
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

/* ── Insight ── */
.insight-retro {
    border-left: 4px solid #ffd700;
    background: linear-gradient(90deg, rgba(255,215,0,0.05), transparent);
    padding: 14px 18px;
    border-radius: 0 12px 12px 0;
    color: #ccccff;
    line-height: 1.6;
    font-family: 'Trebuchet MS', sans-serif;
}

/* ── Divider ── */
.retro-divider {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00f0ff, #ffd700, #ff00aa, transparent);
    margin: 1.2rem 0;
}

/* ── Muted text ── */
.muted {
    color: #666688;
    font-family: 'Trebuchet MS', sans-serif;
    line-height: 1.6;
}

/* ── Streamlit overrides ── */
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


# ──────────────────────────────────────────────
#  DATA HELPERS
# ──────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_team_list():
    """Get sorted team list. Tries rankings first, falls back to results."""
    try:
        rankings = pd.read_csv("data/rankings.csv")
        if "country_full" in rankings.columns:
            return sorted(rankings["country_full"].dropna().unique().tolist())
    except FileNotFoundError:
        pass
    return get_all_teams()


def compute_h2h(team_a: str, team_b: str, max_matches: int = 20) -> dict:
    """Calculate head-to-head record from results.csv."""
    try:
        df = pd.read_csv("data/results.csv")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    except FileNotFoundError:
        return {"matches": 0}

    # Find all matches between the two teams
    mask = (
        ((df["home_team"] == team_a) & (df["away_team"] == team_b)) |
        ((df["home_team"] == team_b) & (df["away_team"] == team_a))
    )
    h2h = df[mask].sort_values("date", ascending=False).head(max_matches)

    if h2h.empty:
        return {"matches": 0}

    wins_a = 0
    wins_b = 0
    draws = 0
    recent = []

    for _, row in h2h.iterrows():
        hs = row.get("home_score", 0)
        aws = row.get("away_score", 0)
        ht = row.get("home_team", "")

        if hs > aws:
            winner = ht
        elif aws > hs:
            winner = row.get("away_team", "")
            winner = None

        if winner == team_a:
            wins_a += 1
        elif winner == team_b:
            wins_b += 1
            draws += 1

        # Last 5 for display
        if len(recent) < 5:
            recent.append({
                "date": str(row.get("date", ""))[:10],
                "home": ht,
                "away": row.get("away_team", ""),
                "score": f"{int(hs)}-{int(aws)}",
                "tournament": row.get("tournament", ""),
            })

    return {
        "matches": len(h2h),
        "wins_a": wins_a,
        "wins_b": wins_b,
        "draws": draws,
        "recent": recent,
    }


def safe_json(result: dict) -> dict:
    """Convert numpy types for JSON serialization."""
    clean = {}
    for k, v in result.items():
        if isinstance(v, np.ndarray):
            clean[k] = f"[array shape={v.shape}]"
        elif isinstance(v, (np.integer,)):
            clean[k] = int(v)
        elif isinstance(v, (np.floating,)):
            clean[k] = float(v)
            clean[k] = v
    return clean


# ──────────────────────────────────────────────
#  HTML BUILDERS
# ──────────────────────────────────────────────

def get_match_badge(match_type: str) -> str:
    badges = {
        "⚔️ Elite Clash":       '<span class="match-badge badge-elite">⚔️🔥 ELITE CLASH 🔥⚔️</span>',
        "🔻 Total Mismatch":    '<span class="match-badge badge-mismatch">💀 TOTAL MISMATCH 💀</span>',
        "📊 Clear Favorite":    '<span class="match-badge badge-favorite">👑 CLEAR FAVORITE 👑</span>',
        "🔥 Top Team Showdown": '<span class="match-badge badge-showdown">🔥 TOP TEAM SHOWDOWN 🔥</span>',
        "⚡ Competitive Match":  '<span class="match-badge badge-competitive">⚡ COMPETITIVE ⚡</span>',
        # Fallbacks for v6 engine format (no emojis)
        "Elite Clash":       '<span class="match-badge badge-elite">⚔️🔥 ELITE CLASH 🔥⚔️</span>',
        "Total Mismatch":    '<span class="match-badge badge-mismatch">💀 TOTAL MISMATCH 💀</span>',
        "Clear Favorite":    '<span class="match-badge badge-favorite">👑 CLEAR FAVORITE 👑</span>',
        "Competitive Match": '<span class="match-badge badge-competitive">⚡ COMPETITIVE ⚡</span>',
    }
    return badges.get(match_type, '<span class="match-badge badge-competitive">⚽ MATCH ⚽</span>')


def get_venue_badge(is_neutral: bool) -> str:
    if is_neutral:
        return '<span class="match-badge badge-venue">🏟️ NEUTRAL VENUE 🏟️</span>'
    return '<span class="match-badge badge-venue">🏠 HOME ADVANTAGE 🏠</span>'


def build_stars_html(players: list, atk_boost: float, def_boost: float = 1.0) -> str:
    if not players:
        return '<div class="muted">No star player data</div>'
    h = f'<div style="color:#ffd700;font-weight:700;margin-bottom:6px;">'
    h += f'⚔️ ATK: x{atk_boost:.2f}'
    if def_boost and def_boost != 1.0:
        h += f' &nbsp;|&nbsp; 🛡️ DEF: x{def_boost:.2f}'
    h += '</div>'
    for p in players[:5]:
        h += f'<span class="star-player">🌟 {p}</span>'
    return h


def build_h2h_html(h2h: dict, team_a: str, team_b: str) -> str:
    if h2h["matches"] == 0:
        return '<div class="muted">🤷 No previous meetings found in database</div>'

    wa = h2h["wins_a"]
    wb = h2h["wins_b"]
    d = h2h["draws"]
    total = wa + wb + d
    if total == 0:
        total = 1

    pct_a = round(100 * wa / total)
    pct_d = round(100 * d / total)
    pct_b = max(0, 100 - pct_a - pct_d)

    out = f'<div style="color:#8888cc;margin-bottom:8px;">📊 Last <b>{h2h["matches"]}</b> meetings</div>'
    out += '<div class="h2h-bar">'
    if pct_a > 0:
        out += f'<div class="h2h-win" style="width:{pct_a}%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">{wa}W</div>'
    if pct_d > 0:
        out += f'<div class="h2h-draw" style="width:{pct_d}%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">{d}D</div>'
    if pct_b > 0:
        out += f'<div class="h2h-loss" style="width:{pct_b}%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:900;color:#0a0a2e;">{wb}W</div>'
    out += '</div>'

    out += '<div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-top:4px;">'
    out += f'<span style="color:#00f0ff;">🏆 {team_a}</span>'
    out += '<span style="color:#ffd700;">🤝 Draws</span>'
    out += f'<span style="color:#ff00aa;">🏆 {team_b}</span></div>'

    # Recent matches
    recent = h2h.get("recent", [])
    if recent:
        out += '<div style="margin-top:12px;font-size:0.8rem;">'
        for m in recent:
            out += (
                f'<div style="color:#8888cc;padding:2px 0;">'
                f'{m["date"]} — <b style="color:#e0e0ff;">{m["home"]} {m["score"]} {m["away"]}</b>'
                f' <span style="color:#666688;">[{m["tournament"]}]</span></div>'
            )
        out += '</div>'

    return out


def build_match_insight(result: dict, team_a: str, team_b: str) -> str:
    a = result["team_a_win"]
    b = result["team_b_win"]
    d = result["draw"]
    la = result["team_a_lambda"]
    lb = result["team_b_lambda"]
    mt = result.get("match_type", "Competitive")

    lines = [f"<b>{mt}</b>"]

    # Edge assessment
    if abs(a - b) <= 6:
        lines.append(f"🤜🤛 {team_a} and {team_b} are neck and neck — this could go either way!")
    elif a > b:
        margin = a - b
        if margin > 25:
            lines.append(f"💪 {team_a} are heavy favorites ({a:.0f}% vs {b:.0f}%).")
            lines.append(f"📈 {team_a} have the edge, but {team_b} can't be counted out.")
        margin = b - a
        if margin > 25:
            lines.append(f"💪 {team_b} are heavy favorites ({b:.0f}% vs {a:.0f}%).")
            lines.append(f"📈 {team_b} have the edge, but {team_a} are dangerous.")

    # Draw assessment
    if d >= 27:
        lines.append("🤝 High draw probability — expect a cagey affair.")
    elif d <= 18:
        lines.append("⚡ Low draw chance — someone's winning this one.")

    # Goals assessment
    total_xg = la + lb
    if total_xg >= 3.0:
        lines.append(f"🔥 Goal fest alert! Combined xG of {total_xg:.1f} — expect fireworks.")
    elif total_xg <= 2.2:
        lines.append(f"🔒 Tight, tactical battle expected (combined xG: {total_xg:.1f}).")
        lines.append(f"⚽ Expect 2-3 goals in a balanced contest (combined xG: {total_xg:.1f}).")

    return "<br>".join(lines)


# ──────────────────────────────────────────────
#  MAIN UI
# ──────────────────────────────────────────────

teams = get_team_list()

if not teams:
    st.error("No team data found. Run `python get_data.py` first.")
    st.stop()

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-title">⚽ Mundialista AI ⚽</div>
    <div class="hero-subtitle">World Cup 2026 Match Intelligence</div>
    <div class="hero-tag">Dixon-Coles Poisson Model • 49,000+ Historical Matches • Monte Carlo Simulation</div>
</div>
""", unsafe_allow_html=True)

# ── Match Setup Card ──
st.markdown('<div class="retro-card"><div class="retro-card-title">🎮 Match Setup</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 0.6])
with col1:
    idx_a = teams.index("Argentina") if "Argentina" in teams else 0
    team_a = st.selectbox("Home / Team A", teams, index=idx_a)
with col2:
    idx_b = teams.index("Brazil") if "Brazil" in teams else min(1, len(teams) - 1)
    team_b = st.selectbox("Away / Team B", teams, index=idx_b)
with col3:
    neutral = st.checkbox("Neutral venue", value=True)
    run_prediction = st.button("⚽ Generate Prediction")
st.markdown("</div>", unsafe_allow_html=True)

# ── Run Prediction ──
if run_prediction:
    if team_a == team_b:
        st.warning("⚠️ Please choose two different teams.")
        try:
            with st.spinner("🧠 Analyzing match data and running simulations..."):
                # FIX: Actually pass home advantage!
                home = None if neutral else team_a
                result = predict(team_a, team_b, home=home)
                charts = generate_all_charts(result, team_a, team_b)
                h2h = compute_h2h(team_a, team_b)

                st.session_state["result"] = result
                st.session_state["charts"] = charts
                st.session_state["h2h"] = h2h
                st.session_state["pred_a"] = team_a
                st.session_state["pred_b"] = team_b
                st.session_state["neutral"] = neutral
        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
            import traceback
            st.code(traceback.format_exc())

# ── Display Results ──
if "result" in st.session_state:
    result = st.session_state["result"]
    charts = st.session_state.get("charts", {})
    h2h = st.session_state.get("h2h", {"matches": 0})
    da = st.session_state["pred_a"]
    db = st.session_state["pred_b"]
    is_neutral = st.session_state.get("neutral", True)

    rk_a = result.get("team_a_rank", "N/A")
    rk_b = result.get("team_b_rank", "N/A")
    la = result.get("team_a_lambda", 0.0)
    lb = result.get("team_b_lambda", 0.0)
    mt = result.get("match_type", "Competitive")
    ts = result.get("top_scores", [])[:5]
    wa = f"{result['team_a_win']:.1f}"
    dv = f"{result['draw']:.1f}"
    wb = f"{result['team_b_win']:.1f}"

    # ── Main Result Card ──
    st.markdown('<div class="retro-card">', unsafe_allow_html=True)

    # VS Header
    st.markdown(f"""
    <div class="vs-line">
        <div>
            <div class="team-name">{da}</div>
            <div class="team-rank">FIFA Rank #{rk_a}</div>
        </div>
        <div class="vs-center">VS</div>
        <div style="text-align:right;">
            <div class="team-name">{db}</div>
            <div class="team-rank">FIFA Rank #{rk_b}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Badges
    st.markdown(
        get_match_badge(mt) + " " + get_venue_badge(is_neutral),
        unsafe_allow_html=True,
    )

    # Win Probability Metrics
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box">
            <div class="metric-label">{da} Win</div>
            <div class="metric-value">{wa}%</div>
            <div class="metric-sub">Analytical probability</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Draw</div>
            <div class="metric-value metric-value-gold">{dv}%</div>
            <div class="metric-sub">Stalemate probability</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">{db} Win</div>
            <div class="metric-value metric-value-pink">{wb}%</div>
            <div class="metric-sub">Analytical probability</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Probability Bars
    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="retro-card-title">📊 Win Probability</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="prob-wrap">
        <div class="prob-label-row"><span>{da} Win</span><span>{wa}%</span></div>
        <div class="prob-track"><div class="prob-fill-cyan" style="width:{wa}%;"></div></div>
        <div class="prob-label-row"><span>Draw</span><span>{dv}%</span></div>
        <div class="prob-track"><div class="prob-fill-gold" style="width:{dv}%;"></div></div>
        <div class="prob-label-row"><span>{db} Win</span><span>{wb}%</span></div>
        <div class="prob-track"><div class="prob-fill-pink" style="width:{wb}%;"></div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)

    # ── Star Players (two columns) ──
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(f'<div class="retro-card retro-card-gold"><div class="retro-card-title">🌟 {da} Stars</div>', unsafe_allow_html=True)
        st.markdown(
            build_stars_html(
                result.get("team_a_stars", []),
                result.get("team_a_star_boost", 1.0),
                result.get("team_a_def_boost", 1.0),
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with sc2:
        st.markdown(f'<div class="retro-card retro-card-gold"><div class="retro-card-title">🌟 {db} Stars</div>', unsafe_allow_html=True)
        st.markdown(
            build_stars_html(
                result.get("team_b_stars", []),
                result.get("team_b_star_boost", 1.0),
                result.get("team_b_def_boost", 1.0),
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Head to Head (REAL DATA!) ──
    st.markdown(
        '<div class="retro-card retro-card-pink">'
        '<div class="retro-card-title">⚔️ Head-to-Head</div>',
        unsafe_allow_html=True,
    )
    st.markdown(build_h2h_html(h2h, da, db), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Expected Goals + Top Scores ──
    s1, s2 = st.columns(2)
    with s1:
        st.markdown('<div class="retro-card"><div class="retro-card-title">⚽ Expected Goals</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box">
                <div class="metric-label">{da}</div>
                <div class="metric-value">{la:.2f}</div>
                <div class="metric-sub">xG (expected goals)</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">{db}</div>
                <div class="metric-value metric-value-pink">{lb:.2f}</div>
                <div class="metric-sub">xG (expected goals)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with s2:
        st.markdown('<div class="retro-card"><div class="retro-card-title">🎯 Most Likely Scores</div>', unsafe_allow_html=True)
        if ts:
            pills = ""
            for i, sc in enumerate(ts):
                if isinstance(sc, (list, tuple)) and len(sc) >= 2:
                    scoreline = str(sc[0])
                    pct = sc[1]
                    # Format: "1-0 (15.2%)" for v7, "1-0 (x1530)" for v6
                    if isinstance(pct, float) and pct < 1:
                        label = f"{scoreline} ({pct*100:.1f}%)"
                    elif isinstance(pct, float):
                        label = f"{scoreline} ({pct:.1f}%)"
                        label = f"{scoreline}"
                    css_class = "score-pill-top" if i == 0 else "score-pill"
                    pills += f'<span class="{css_class}">{label}</span>'
            st.markdown(pills, unsafe_allow_html=True)
            st.markdown('<div class="muted">No scoreline data available.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── AI Insight ──
    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)
    ins = build_match_insight(result, da, db)
    st.markdown('<div class="retro-card-title">🧠 AI Match Insight</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-retro">{ins}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Close main result card

    # ── Visual Analytics ──
    st.markdown('<div class="retro-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="retro-card"><div class="retro-card-title">📈 Visual Analytics</div>',
        unsafe_allow_html=True,
    )

    chart_tabs = st.tabs([
        "📋 Summary Card",
        "📊 Win Probability",
        "🔢 Score Matrix",
        "🎯 Top Scorelines",
        "📈 Goal Distribution",
    ])

    chart_keys = ["summary", "probability", "matrix", "top_scores", "goals"]

    for tab, key in zip(chart_tabs, chart_keys):
        with tab:
            path = charts.get(key, "")
            if path and os.path.exists(path):
                st.image(path, use_container_width=True)  # FIX: correct parameter
                st.info(f"📭 {key.title()} chart not available.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Download Report ──
    if "html" in charts and os.path.exists(charts["html"]):
        with open(charts["html"], "r", encoding="utf-8") as f:
            html_content = f.read()
        st.download_button(
            label="📥 Download Full HTML Report",
            data=html_content,
            file_name=f"mundialista_{da}_vs_{db}.html",
            mime="text/html",
        )

    # ── Simulation Cross-Check (if v7 engine) ──
    if "sim_team_a_win" in result:
        with st.expander("🔬 Simulation Cross-Check"):
            st.markdown(f"""
            **Analytical Model** vs **Monte Carlo ({result.get('n_simulations', 'N/A'):,} simulations)**

            | Outcome | Analytical | Simulation |
            |---------|-----------|------------|
            | {da} Win | {result['team_a_win']:.1f}% | {result.get('sim_team_a_win', 'N/A')}% |
            | Draw | {result['draw']:.1f}% | {result.get('sim_draw', 'N/A')}% |
            | {db} Win | {result['team_b_win']:.1f}% | {result.get('sim_team_b_win', 'N/A')}% |

            *Close agreement confirms model stability.*
            """)

    # ── Raw Data (safe JSON) ──
    with st.expander("🔧 Raw Prediction Output"):
        st.json(safe_json(result))  # FIX: won't crash on numpy


    # ── Welcome Screen ──
    st.markdown("""
    <div class="retro-card">
        <div class="retro-card-title">🎮 How To Play</div>
        <div class="muted">
            Select two national teams, choose whether the match is on neutral ground, 
            and click <strong style="color:#ffd700;">Generate Prediction</strong> to view:<br><br>
            ⚽ Win probabilities & expected goals<br>
            🎯 Most likely scorelines<br>
            ⚔️ Head-to-head history<br>
            🌟 Star player impact analysis<br>
            🧠 AI-generated match insight<br>
            📈 Full visual analytics charts
        </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  SIDEBAR: Admin Panel
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<div class="retro-card-title">🛠️ Admin Panel</div>',
        unsafe_allow_html=True,
    )

    # ── Add Recent Result ──
    with st.expander("➕ Add Recent Result"):
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
                csv_path = "data/recent_results.csv"
                try:
                    rdf = pd.read_csv(csv_path)
                except FileNotFoundError:
                    rdf = pd.DataFrame(columns=[
                        "date", "home_team", "away_team", "home_score",
                        "away_score", "tournament", "city", "country", "neutral",
                    ])
                new_row = pd.DataFrame([{
                    "date": ad_date,
                    "home_team": ad_home,
                    "away_team": ad_away,
                    "home_score": int(ad_hscore),
                    "away_score": int(ad_ascore),
                    "tournament": ad_tourn,
                    "city": "",
                    "country": "",
                    "neutral": ad_neutral,
                }])
                rdf = pd.concat([rdf, new_row], ignore_index=True)
                rdf.to_csv(csv_path, index=False)

                # Clear caches
                try:
                    from prediction_engine import _data
                    _data.clear_cache()
                except Exception:
                    pass
                get_team_list.clear()

                st.success(f"✅ {ad_home} {int(ad_hscore)}-{int(ad_ascore)} {ad_away} saved!")
                st.warning("⚠️ Enter both team names!")

    # ── View Recent Results ──
    with st.expander("📋 View Recent Results"):
        try:
            rdf_view = pd.read_csv("data/recent_results.csv")
            if rdf_view.empty:
                st.info("No recent results yet.")
                for _, rv in rdf_view.iterrows():
                    st.markdown(
                        f'<span style="color:#00f0ff;">{rv["date"]}</span> '
                        f'<b style="color:#ffd700;">{rv["home_team"]} '
                        f'{rv["home_score"]}-{rv["away_score"]} {rv["away_team"]}</b> '
                        f'<span style="color:#8888cc;">[{rv["tournament"]}]</span>',
                        unsafe_allow_html=True,
                    )
        except FileNotFoundError:
            st.info("No recent results file found.")

    # ── Card Predictor ──
    with st.expander("🟥 Card Predictor"):
        cp_col1, cp_col2 = st.columns(2)
        with cp_col1:
            cp_a = st.selectbox("Team A", teams, index=0, key="card_a")
        with cp_col2:
            cp_b_idx = min(1, len(teams) - 1)
            cp_b = st.selectbox("Team B", teams, index=cp_b_idx, key="card_b")

        if st.button("🟥 Predict Cards"):
            if cp_a != cp_b:
                try:
                    from prediction_engine import get_team_stats as gts

                    s_a = gts(cp_a)
                    s_b = gts(cp_b)
                    r_a = get_team_ranking(cp_a)
                    r_b = get_team_ranking(cp_b)
                    rank_gap = abs(r_a - r_b)

                    intensity = 1.25 if rank_gap < 15 else (0.85 if rank_gap > 50 else 1.0)
                    base_yellow = 2.8
                    agg_a = s_a.get("defense", 1.0) * 0.6 + s_a.get("avg_ga", 1.36) * 0.2
                    agg_b = s_b.get("defense", 1.0) * 0.6 + s_b.get("avg_ga", 1.36) * 0.2

                    y_a = base_yellow * 0.5 * intensity * agg_a
                    y_b = base_yellow * 0.5 * intensity * agg_b
                    total_y = y_a + y_b

                    red_factor = intensity * (1.3 if total_y > 4.0 else 1.0)
                    red_prob = min(0.08 * red_factor * 2 * 4, 0.35)

                    st.markdown('<div class="retro-card">', unsafe_allow_html=True)
                    st.markdown('<div class="retro-card-title">🟥 Card Forecast</div>', unsafe_allow_html=True)
                    st.markdown(
                        f'🟨 <b style="color:#ffd700;">{cp_a}</b>: ~{y_a:.1f} yellows<br>'
                        f'🟨 <b style="color:#ffd700;">{cp_b}</b>: ~{y_b:.1f} yellows<br>'
                        f'🟨 Total: ~{total_y:.1f} yellows<br>'
                        f'🟥 Red probability: <b>{100*red_prob:.1f}%</b>',
                        unsafe_allow_html=True,
                    )
                    if red_prob > 0.25:
                        st.markdown('🟥 <b style="color:#ff3333;">HIGH red card risk! Heated match!</b>', unsafe_allow_html=True)
                    elif red_prob > 0.15:
                        st.markdown('🟨 <b style="color:#ffd700;">Moderate red card risk.</b>', unsafe_allow_html=True)
                        st.markdown('🟩 <b style="color:#00ff88;">Low red card risk.</b>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── Clear Data ──
    with st.expander("🗑️ Clear Recent Data"):
        if st.button("Clear ALL recent results"):
            for path, cols in [
                ("data/recent_results.csv", ["date","home_team","away_team","home_score","away_score","tournament","city","country","neutral"]),
                ("data/recent_goalscorers.csv", ["date","home_team","away_team","team","scorer","minute","own_goal","penalty"]),
            ]:
                pd.DataFrame(columns=cols).to_csv(path, index=False)
            try:
                from prediction_engine import _data
                _data.clear_cache()
            except Exception:
                pass
            get_team_list.clear()
            st.success("🗑️ All recent data cleared!")