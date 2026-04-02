print("=" * 60)
print("  UPGRADING STREAMLIT APP WITH NEW FEATURES")
print("=" * 60)

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

with open('app_backup.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Backup saved to app_backup.py")

changes = 0

# 1. Add new imports
old_imports = 'from strength_adjust import compute_team_ratings, get_adjusted_stats'
new_imports = '''from strength_adjust import compute_team_ratings, get_adjusted_stats
from data_loader import get_team_ranking
from player_impact import get_team_star_impact, get_player_summary, STAR_PLAYERS'''

if old_imports in code and 'get_team_ranking' not in code:
    code = code.replace(old_imports, new_imports)
    print("1. Added imports: get_team_ranking, player_impact")
    changes += 1
else:
    print("1. Imports already present or pattern not found")

# 2. Update shrinkage from 8 to 10
if 'shrink_k=8' in code:
    code = code.replace('shrink_k=8', 'shrink_k=10')
    print("2. Updated shrinkage k=8 -> k=10")
    changes += 1
else:
    print("2. shrink_k=8 not found (may already be updated)")

# 3. Add FIFA Rankings + Star Players panel to sidebar
# Find where sidebar ends, add our new sections
old_sidebar_end = 'st.sidebar.caption("**Engine:** Inhomogeneous Poisson + Bayesian PyMC")'
new_sidebar = '''st.sidebar.caption("**Engine:** Inhomogeneous Poisson + Bayesian PyMC")
    
    # FIFA Rankings Panel
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🏆 FIFA Rankings**")
    try:
        h_rank_info = get_team_ranking(home_team)
        a_rank_info = get_team_ranking(away_team)
        h_rank = h_rank_info.get('rank', '?') if isinstance(h_rank_info, dict) else '?'
        a_rank = a_rank_info.get('rank', '?') if isinstance(a_rank_info, dict) else '?'
        h_pts = h_rank_info.get('total_points', 0) if isinstance(h_rank_info, dict) else 0
        a_pts = a_rank_info.get('total_points', 0) if isinstance(a_rank_info, dict) else 0
        st.sidebar.markdown(f"  {home_team}: **#{h_rank}** ({h_pts:.0f} pts)")
        st.sidebar.markdown(f"  {away_team}: **#{a_rank}** ({a_pts:.0f} pts)")
    except Exception:
        st.sidebar.caption("Rankings unavailable")
    
    # Star Players Panel
    st.sidebar.markdown("---")
    st.sidebar.markdown("**⭐ Star Players**")
    for team_name in [home_team, away_team]:
        star_mult = get_team_star_impact(team_name)
        if team_name in STAR_PLAYERS:
            active = [p for p, info in STAR_PLAYERS[team_name].items() if info["status"] == "active"]
            stars_str = ", ".join(active[:3])
            st.sidebar.markdown(f"  {team_name}: {stars_str} ({star_mult:.0%} boost)")
        else:
            st.sidebar.markdown(f"  {team_name}: No tracked stars")'''

if old_sidebar_end in code and 'FIFA Rankings Panel' not in code:
    code = code.replace(old_sidebar_end, new_sidebar)
    print("3. Added FIFA Rankings + Star Players to sidebar")
    changes += 1
else:
    print("3. Sidebar panels already exist or pattern not found")

# 4. Add ranking adjustment to the strength computation
# Find compute_global_priors or the stats computation
# We'll add a ranking factor to the attack/defense estimates

# 5. Add a Rankings & Stars tab to main content
# Find where results are displayed
results_header = 'st.header(f"🏆 {home_team}  vs  {away_team} — Prediction Results")'
if results_header in code and 'Rankings Insight' not in code:
    new_results = results_header + '''
    
    # Rankings & Star Player Insight
    try:
        import math
        h_ri = get_team_ranking(home_team)
        a_ri = get_team_ranking(away_team)
        h_r = h_ri.get('rank', 100) if isinstance(h_ri, dict) else 100
        a_r = a_ri.get('rank', 100) if isinstance(a_ri, dict) else 100
        rank_gap = abs(h_r - a_r)
        
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric(f"🏆 {home_team} Rank", f"#{h_r}")
        with col_r2:
            if rank_gap < 15:
                st.metric("Match Type", "⚔️ Elite Clash")
            elif rank_gap < 40:
                st.metric("Match Type", "📊 Clear Favorite")
            else:
                st.metric("Match Type", "🔥 Major Mismatch")
        with col_r3:
            st.metric(f"🏆 {away_team} Rank", f"#{a_r}")
        
        # Star players display
        h_stars = STAR_PLAYERS.get(home_team, {})
        a_stars = STAR_PLAYERS.get(away_team, {})
        if h_stars or a_stars:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if h_stars:
                    st.markdown(f"**⭐ {home_team} Key Players:**")
                    for p, info in h_stars.items():
                        if info["status"] == "active":
                            boost = (info["attack"] - 1) * 100
                            st.markdown(f"- {p} (+{boost:.0f}%)")
            with col_s2:
                if a_stars:
                    st.markdown(f"**⭐ {away_team} Key Players:**")
                    for p, info in a_stars.items():
                        if info["status"] == "active":
                            boost = (info["attack"] - 1) * 100
                            st.markdown(f"- {p} (+{boost:.0f}%)")
        st.markdown("---")
    except Exception as e:
        pass  # Silently skip if rankings unavailable
    '''
    code = code.replace(results_header, new_results)
    print("4. Added Rankings & Stars insight to results page")
    changes += 1
else:
    print("4. Results section not found or already updated")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

import py_compile
try:
    py_compile.compile('app.py', doraise=True)
    print(f"\nSYNTAX CHECK: OK ({changes} changes applied)")
except py_compile.PyCompileError as e:
    print(f"\nSYNTAX ERROR: {e}")
    with open('app_backup.py', 'r', encoding='utf-8') as f:
        backup = f.read()
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(backup)
    print("Backup restored!")
    exit()

print("\nUpgrades applied! Test with: streamlit run app.py")
print("New features in the app:")
print("  📊 FIFA Rankings shown in sidebar")
print("  ⭐ Star players listed for each team")
print("  🏆 Match type indicator (Elite Clash / Clear Favorite / Mismatch)")
print("  📈 Key player impact percentages")
