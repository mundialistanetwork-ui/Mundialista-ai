# app.py - Streamlit web interface using shared prediction engine
"""
Streamlit web app for Mundialista-AI.
Uses the same prediction engine as CLI for consistent results.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from prediction_engine import predict, get_score_matrix, CONFIG, get_all_teams, STAR_PLAYERS

# ============== PAGE CONFIG ==============
st.set_page_config(
    page_title="Mundialista-AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== CUSTOM CSS ==============
st.markdown("""
<style>
    .big-number { font-size: 48px; font-weight: bold; text-align: center; }
    .blue { color: #3498db; }
    .gray { color: #95a5a6; }
    .red { color: #e74c3c; }
    .match-type { 
        padding: 5px 15px; 
        border-radius: 20px; 
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }
    .elite { background: #f39c12; color: white; }
    .competitive { background: #3498db; color: white; }
    .favorite { background: #9b59b6; color: white; }
    .mismatch { background: #e74c3c; color: white; }
</style>
""", unsafe_allow_html=True)

# ============== HEADER ==============
st.title("Mundialista-AI Predictions")
st.caption(f"Powered by {CONFIG['N_SIMULATIONS']:,} Poisson simulations | Same engine as CLI")

# ============== SIDEBAR ==============
st.sidebar.header("Match Setup")

# Load teams
@st.cache_data
def load_teams():
    return get_all_teams()

all_teams = load_teams()

if not all_teams:
    st.error("No teams found! Check that data/results.csv exists.")
    st.stop()

# Team selection
col1, col2 = st.sidebar.columns(2)
with col1:
    default_a = all_teams.index("Argentina") if "Argentina" in all_teams else 0
    team_a = st.selectbox("Team A", all_teams, index=default_a)
with col2:
    default_b = all_teams.index("Brazil") if "Brazil" in all_teams else 1
    team_b = st.selectbox("Team B", all_teams, index=default_b)

# Home team
home_option = st.sidebar.radio(
    "Home Team",
    [team_a, team_b, "Neutral"],
    index=2,
    horizontal=True
)
home = None if home_option == "Neutral" else home_option

# Run prediction button
run_prediction = st.sidebar.button("Predict Match", type="primary", use_container_width=True)

# ============== MAIN CONTENT ==============
if run_prediction or 'last_teams' not in st.session_state or st.session_state.last_teams != (team_a, team_b, home):
    with st.spinner(f"Running {CONFIG['N_SIMULATIONS']:,} simulations..."):
        result = predict(team_a, team_b, home=home)
        st.session_state.result = result
        st.session_state.last_teams = (team_a, team_b, home)

if 'result' in st.session_state:
    result = st.session_state.result
    
    # ============== SIDEBAR INFO ==============
    st.sidebar.divider()
    
    # Rankings
    st.sidebar.subheader("FIFA Rankings")
    r_col1, r_col2 = st.sidebar.columns(2)
    with r_col1:
        st.metric(result['team_a'], f"#{result['team_a_rank']}", f"{result['team_a_points']} pts")
    with r_col2:
        st.metric(result['team_b'], f"#{result['team_b_rank']}", f"{result['team_b_points']} pts")
    
    # Match Type
    match_type_colors = {
        'Elite Clash': 'elite',
        'Competitive Match': 'competitive', 
        'Clear Favorite': 'favorite',
        'Total Mismatch': 'mismatch',
    }
    mt_class = match_type_colors.get(result['match_type'], 'competitive')
    st.sidebar.markdown(f"<div class='match-type {mt_class}'>{result['match_type']}</div>", 
                       unsafe_allow_html=True)
    st.sidebar.caption(f"Rank gap: {result['rank_gap']} positions")
    
    # Star Players
    st.sidebar.divider()
    st.sidebar.subheader("Star Players")
    
    stars_a = result['team_a_stars']
    stars_b = result['team_b_stars']
    boost_a = (result['team_a_star_boost'] - 1) * 100
    boost_b = (result['team_b_star_boost'] - 1) * 100
    
    st.sidebar.write(f"**{result['team_a']}** (+{boost_a:.0f}% boost)")
    if stars_a:
        for star in stars_a[:3]:
            st.sidebar.write(f"  - {star}")
    else:
        st.sidebar.write("  - No tracked stars")
    
    st.sidebar.write(f"**{result['team_b']}** (+{boost_b:.0f}% boost)")
    if stars_b:
        for star in stars_b[:3]:
            st.sidebar.write(f"  - {star}")
    else:
        st.sidebar.write("  - No tracked stars")
    
    # ============== MAIN RESULTS ==============
    st.header(f"{result['team_a']} vs {result['team_b']}")
    
    if result['home']:
        st.caption(f"Home: {result['home']}")
    else:
        st.caption("Neutral Venue")
    
    # Big probability numbers
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"<div class='big-number blue'>{result['team_a_win']}%</div>", 
                   unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{result['team_a']} Win</p>", 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div class='big-number gray'>{result['draw']}%</div>", 
                   unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Draw</p>", 
                   unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<div class='big-number red'>{result['team_b_win']}%</div>", 
                   unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{result['team_b']} Win</p>", 
                   unsafe_allow_html=True)
    
    # ============== PROBABILITY BAR ==============
    st.divider()
    
    fig_bar = go.Figure(go.Bar(
        x=[result['team_a_win'], result['draw'], result['team_b_win']],
        y=[result['team_a'], 'Draw', result['team_b']],
        orientation='h',
        marker_color=['#3498db', '#95a5a6', '#e74c3c'],
        text=[f"{result['team_a_win']}%", f"{result['draw']}%", f"{result['team_b_win']}%"],
        textposition='inside',
        textfont=dict(size=16, color='white'),
    ))
    fig_bar.update_layout(
        title="Win Probabilities",
        xaxis_title="Probability (%)",
        xaxis=dict(range=[0, 100]),
        height=250,
        showlegend=False,
        margin=dict(l=100, r=20, t=50, b=50),
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # ============== TABS FOR CHARTS ==============
    tab1, tab2, tab3, tab4 = st.tabs(["Score Matrix", "Top Scores", "Goal Distribution", "Technical"])
    
    # TAB 1: Score Matrix
    with tab1:
        st.subheader("Score Probability Matrix")
        
        matrix = get_score_matrix(result['team_a_lambda'], result['team_b_lambda'], max_goals=5)
        matrix_pct = matrix * 100
        
        fig_matrix = px.imshow(
            matrix_pct,
            labels=dict(x=f"{result['team_b']} Goals", y=f"{result['team_a']} Goals", color="Probability %"),
            x=[str(i) for i in range(6)],
            y=[str(i) for i in range(6)],
            color_continuous_scale="Blues",
            aspect="equal",
            text_auto='.1f',
        )
        fig_matrix.update_layout(height=500)
        fig_matrix.update_traces(texttemplate='%{z:.1f}%', textfont=dict(size=12))
        st.plotly_chart(fig_matrix, use_container_width=True)
    
    # TAB 2: Top Scores
    with tab2:
        st.subheader("Most Likely Scorelines")
        
        top_scores = result['top_scores'][:8]
        n_sims = result['n_simulations']
        
        scores = [s[0] for s in top_scores]
        percentages = [100 * s[1] / n_sims for s in top_scores]
        
        colors = []
        for score in scores:
            parts = score.split('-')
            a, b = int(parts[0]), int(parts[1])
            if a > b:
                colors.append('#3498db')
            elif b > a:
                colors.append('#e74c3c')
            else:
                colors.append('#95a5a6')
        
        fig_scores = go.Figure(go.Bar(
            x=scores,
            y=percentages,
            marker_color=colors,
            text=[f'{p:.1f}%' for p in percentages],
            textposition='outside',
        ))
        fig_scores.update_layout(
            xaxis_title="Scoreline",
            yaxis_title="Probability (%)",
            height=400,
            showlegend=False,
        )
        st.plotly_chart(fig_scores, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        col1.markdown(f":blue_circle: {result['team_a']} Win")
        col2.markdown(":white_circle: Draw")
        col3.markdown(f":red_circle: {result['team_b']} Win")
    
    # TAB 3: Goal Distribution
    with tab3:
        st.subheader("Goal Distribution")
        
        goals_a = result['goals_a']
        goals_b = result['goals_b']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist_a = px.histogram(
                x=goals_a, 
                nbins=10,
                title=f"{result['team_a']} Goals",
                labels={'x': 'Goals', 'y': 'Frequency'},
                color_discrete_sequence=['#3498db'],
            )
            fig_hist_a.add_vline(x=result['team_a_lambda'], line_dash="dash", 
                                line_color="red", annotation_text=f"Expected: {result['team_a_lambda']:.2f}")
            fig_hist_a.update_Write-Host "Continuing setup..." -ForegroundColor Cyan

# ============================================================
# FILE 4: app.py (Streamlit) - COMPLETE VERSION
# ============================================================

Write-Host "[5/6] Creating app.py (complete)..." -ForegroundColor Yellow

$appStreamlit = @'
# app.py - Streamlit web interface using shared prediction engine
"""
Streamlit web app for Mundialista-AI.
Uses the same prediction engine as CLI for consistent results.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from prediction_engine import predict, get_score_matrix, CONFIG, get_all_teams, STAR_PLAYERS

# ============== PAGE CONFIG ==============
st.set_page_config(
    page_title="Mundialista-AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== CUSTOM CSS ==============
st.markdown("""
<style>
    .big-number { font-size: 48px; font-weight: bold; text-align: center; }
    .blue { color: #3498db; }
    .gray { color: #95a5a6; }
    .red { color: #e74c3c; }
    .match-type { 
        padding: 5px 15px; 
        border-radius: 20px; 
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }
    .elite { background: #f39c12; color: white; }
    .competitive { background: #3498db; color: white; }
    .favorite { background: #9b59b6; color: white; }
    .mismatch { background: #e74c3c; color: white; }
</style>
""", unsafe_allow_html=True)

# ============== HEADER ==============
st.title("Mundialista-AI Predictions")
st.caption(f"Powered by {CONFIG['N_SIMULATIONS']:,} Poisson simulations | Same engine as CLI")

# ============== SIDEBAR ==============
st.sidebar.header("Match Setup")

# Load teams
@st.cache_data
def load_teams():
    return get_all_teams()

all_teams = load_teams()

if not all_teams:
    st.error("No teams found! Check that data/results.csv exists.")
    st.stop()

# Team selection
col1, col2 = st.sidebar.columns(2)
with col1:
    default_a = all_teams.index("Argentina") if "Argentina" in all_teams else 0
    team_a = st.selectbox("Team A", all_teams, index=default_a)
with col2:
    default_b = all_teams.index("Brazil") if "Brazil" in all_teams else 1
    team_b = st.selectbox("Team B", all_teams, index=default_b)

# Home team
home_option = st.sidebar.radio(
    "Home Team",
    [team_a, team_b, "Neutral"],
    index=2,
    horizontal=True
)
home = None if home_option == "Neutral" else home_option

# Run prediction button
run_prediction = st.sidebar.button("Predict Match", type="primary", use_container_width=True)

# ============== RUN PREDICTION ==============
if run_prediction or 'last_teams' not in st.session_state or st.session_state.get('last_teams') != (team_a, team_b, home):
    with st.spinner(f"Running {CONFIG['N_SIMULATIONS']:,} simulations..."):
        result = predict(team_a, team_b, home=home)
        st.session_state.result = result
        st.session_state.last_teams = (team_a, team_b, home)

# ============== DISPLAY RESULTS ==============
if 'result' in st.session_state:
    result = st.session_state.result
    
    # ============== SIDEBAR INFO ==============
    st.sidebar.divider()
    
    # Rankings
    st.sidebar.subheader("FIFA Rankings")
    r_col1, r_col2 = st.sidebar.columns(2)
    with r_col1:
        st.metric(result['team_a'], f"#{result['team_a_rank']}", f"{result['team_a_points']} pts")
    with r_col2:
        st.metric(result['team_b'], f"#{result['team_b_rank']}", f"{result['team_b_points']} pts")
    
    # Match Type Badge
    match_type_colors = {
        'Elite Clash': 'elite',
        'Competitive Match': 'competitive', 
        'Clear Favorite': 'favorite',
        'Total Mismatch': 'mismatch',
    }
    mt_class = match_type_colors.get(result['match_type'], 'competitive')
    st.sidebar.markdown(f"<div class='match-type {mt_class}'>{result['match_type']}</div>", 
                       unsafe_allow_html=True)
    st.sidebar.caption(f"Rank gap: {result['rank_gap']} positions")
    
    # Star Players
    st.sidebar.divider()
    st.sidebar.subheader("Star Players")
    
    stars_a = result['team_a_stars']
    stars_b = result['team_b_stars']
    boost_a = (result['team_a_star_boost'] - 1) * 100
    boost_b = (result['team_b_star_boost'] - 1) * 100
    
    st.sidebar.write(f"**{result['team_a']}** (+{boost_a:.0f}% boost)")
    if stars_a:
        for star in stars_a[:3]:
            st.sidebar.write(f"  - {star}")
    else:
        st.sidebar.write("  - No tracked stars")
    
    st.sidebar.write(f"**{result['team_b']}** (+{boost_b:.0f}% boost)")
    if stars_b:
        for star in stars_b[:3]:
            st.sidebar.write(f"  - {star}")
    else:
        st.sidebar.write("  - No tracked stars")
    
    # ============== MAIN RESULTS ==============
    st.header(f"{result['team_a']} vs {result['team_b']}")
    
    if result['home']:
        st.caption(f"Home: {result['home']}")
    else:
        st.caption("Neutral Venue")
    
    # Big probability numbers
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"<div class='big-number blue'>{result['team_a_win']}%</div>", 
                   unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{result['team_a']} Win</p>", 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div class='big-number gray'>{result['draw']}%</div>", 
                   unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Draw</p>", 
                   unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<div class='big-number red'>{result['team_b_win']}%</div>", 
                   unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center'>{result['team_b']} Win</p>", 
                   unsafe_allow_html=True)
    
    # ============== PROBABILITY BAR CHART ==============
    st.divider()
    
    fig_bar = go.Figure(go.Bar(
        x=[result['team_a_win'], result['draw'], result['team_b_win']],
        y=[result['team_a'], 'Draw', result['team_b']],
        orientation='h',
        marker_color=['#3498db', '#95a5a6', '#e74c3c'],
        text=[f"{result['team_a_win']}%", f"{result['draw']}%", f"{result['team_b_win']}%"],
        textposition='inside',
        textfont=dict(size=16, color='white'),
    ))
    fig_bar.update_layout(
        title="Win Probabilities",
        xaxis_title="Probability (%)",
        xaxis=dict(range=[0, 100]),
        height=250,
        showlegend=False,
        margin=dict(l=100, r=20, t=50, b=50),
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # ============== TABS FOR DETAILED CHARTS ==============
    tab1, tab2, tab3, tab4 = st.tabs(["Score Matrix", "Top Scores", "Goal Distribution", "Technical"])
    
    # ---------- TAB 1: SCORE MATRIX ----------
    with tab1:
        st.subheader("Score Probability Matrix")
        st.caption("Each cell shows the probability of that exact scoreline")
        
        matrix = get_score_matrix(result['team_a_lambda'], result['team_b_lambda'], max_goals=5)
        matrix_pct = matrix * 100
        
        fig_matrix = px.imshow(
            matrix_pct,
            labels=dict(x=f"{result['team_b']} Goals", y=f"{result['team_a']} Goals", color="Probability %"),
            x=[str(i) for i in range(6)],
            y=[str(i) for i in range(6)],
            color_continuous_scale="Blues",
            aspect="equal",
            text_auto='.1f',
        )
        fig_matrix.update_layout(height=500)
        fig_matrix.update_traces(texttemplate='%{z:.1f}%', textfont=dict(size=12))
        st.plotly_chart(fig_matrix, use_container_width=True)
    
    # ---------- TAB 2: TOP SCORES ----------
    with tab2:
        st.subheader("Most Likely Scorelines")
        
        top_scores = result['top_scores'][:8]
        n_sims = result['n_simulations']
        
        scores = [s[0] for s in top_scores]
        percentages = [100 * s[1] / n_sims for s in top_scores]
        
        # Color based on winner
        colors = []
        for score in scores:
            parts = score.split('-')
            a, b = int(parts[0]), int(parts[1])
            if a > b:
                colors.append('#3498db')  # Team A wins
            elif b > a:
                colors.append('#e74c3c')  # Team B wins
            else:
                colors.append('#95a5a6')  # Draw
        
        fig_scores = go.Figure(go.Bar(
            x=scores,
            y=percentages,
            marker_color=colors,
            text=[f'{p:.1f}%' for p in percentages],
            textposition='outside',
        ))
        fig_scores.update_layout(
            xaxis_title="Scoreline",
            yaxis_title="Probability (%)",
            height=400,
            showlegend=False,
        )
        st.plotly_chart(fig_scores, use_container_width=True)
        
        # Legend
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"🔵 {result['team_a']} Win")
        col2.markdown("⚪ Draw")
        col3.markdown(f"🔴 {result['team_b']} Win")
    
    # ---------- TAB 3: GOAL DISTRIBUTION ----------
    with tab3:
        st.subheader("Goal Distribution from Simulations")
        
        goals_a = result['goals_a']
        goals_b = result['goals_b']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist_a = px.histogram(
                x=goals_a, 
                nbins=10,
                title=f"{result['team_a']} Goals",
                labels={'x': 'Goals', 'y': 'Frequency'},
                color_discrete_sequence=['#3498db'],
            )
            fig_hist_a.add_vline(
                x=result['team_a_lambda'], 
                line_dash="dash", 
                line_color="red", 
                annotation_text=f"Expected: {result['team_a_lambda']:.2f}"
            )
            fig_hist_a.update_layout(height=350)
            st.plotly_chart(fig_hist_a, use_container_width=True)
        
        with col2:
            fig_hist_b = px.histogram(
                x=goals_b, 
                nbins=10,
                title=f"{result['team_b']} Goals",
                labels={'x': 'Goals', 'y': 'Frequency'},
                color_discrete_sequence=['#e74c3c'],
            )
            fig_hist_b.add_vline(
                x=result['team_b_lambda'], 
                line_dash="dash", 
                line_color="blue", 
                annotation_text=f"Expected: {result['team_b_lambda']:.2f}"
            )
            fig_hist_b.update_layout(height=350)
            st.plotly_chart(fig_hist_b, use_container_width=True)
        
        # Summary stats
        st.caption(f"Based on {n_sims:,} simulated matches")
    
    # ---------- TAB 4: TECHNICAL DETAILS ----------
    with tab4:
        st.subheader("Technical Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Expected Goals (λ)**")
            st.write(f"- {result['team_a']}: {result['team_a_lambda']:.3f}")
            st.write(f"- {result['team_b']}: {result['team_b_lambda']:.3f}")
            
            st.markdown("**Star Player Boosts**")
            st.write(f"- {result['team_a']}: {result['team_a_star_boost']:.1%}")
            st.write(f"- {result['team_b']}: {result['team_b_star_boost']:.1%}")
            
            st.markdown("**Rankings**")
            st.write(f"- {result['team_a']}: #{result['team_a_rank']} ({result['team_a_points']} pts)")
            st.write(f"- {result['team_b']}: #{result['team_b_rank']} ({result['team_b_points']} pts)")
        
        with col2:
            st.markdown("**Engine Configuration**")
            st.write(f"- Simulations: {CONFIG['N_SIMULATIONS']:,}")
            st.write(f"- Shrinkage k: {CONFIG['SHRINK_K']}")
            st.write(f"- Home advantage: {CONFIG['HOME_ADVANTAGE']:.0%}")
            st.write(f"- Ratio cap: {CONFIG['MAX_RATIO']:.0%}")
            st.write(f"- Global baseline: {CONFIG['GLOBAL_GF']}")
            st.write(f"- Form matches: {CONFIG['LAST_N_MATCHES']}")
        
        # Raw simulation data
        with st.expander("View Raw Simulation Data (first 100)"):
            sim_df = pd.DataFrame({
                f'{result["team_a"]} Goals': result['goals_a'][:100],
                f'{result["team_b"]} Goals': result['goals_b'][:100],
            })
            st.dataframe(sim_df, height=300, use_container_width=True)
            st.caption(f"Showing first 100 of {n_sims:,} simulations")

# ============== FOOTER ==============
st.divider()
st.caption(f"Mundialista-AI v4 | {CONFIG['N_SIMULATIONS']:,} Poisson simulations | Same engine as CLI")
st.caption("Built with Streamlit + Plotly | Data: FIFA Rankings + 4,200+ international matches")

