with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
if content.startswith('\ufeff'):
    content = content[1:]
changes = 0

# Add imports at top
if 'from match_manager import' not in content:
    old_import = 'from chart_generator import generate_all_charts'
    new_import = old_import + '\nfrom match_manager import show_recent, estimate_cards, ensure_files'
    content = content.replace(old_import, new_import)
    print("  [1] Added match_manager imports")
    changes += 1

# Add admin panel + card predictor in sidebar
if 'Admin Panel' not in content:
    # Find the else block at the end
    admin_section = '''

# === SIDEBAR: Admin Panel ===
with st.sidebar:
    st.markdown('<div class="retro-card-title">\U0001f6e0\ufe0f Admin Panel \U0001f6e0\ufe0f</div>', unsafe_allow_html=True)

    with st.expander("\u2795 Add Recent Result"):
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

        if st.button("\U0001f4be Save Result"):
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
                st.success("\u2705 " + ad_home + " " + str(int(ad_hscore)) + "-" + str(int(ad_ascore)) + " " + ad_away + " saved!")
            else:
                st.warning("Enter both team names!")

    with st.expander("\U0001f4cb View Recent Results"):
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

    with st.expander("\U0001f7e5 Card Predictor"):
        cp_col1, cp_col2 = st.columns(2)
        with cp_col1:
            cp_a = st.selectbox("Team A", teams, index=0, key="card_a")
        with cp_col2:
            cp_b_idx = 1 if len(teams) > 1 else 0
            cp_b = st.selectbox("Team B", teams, index=cp_b_idx, key="card_b")
        if st.button("\U0001f7e5 Predict Cards"):
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
                    st.markdown('<div class="retro-card-title">\U0001f7e5 Card Forecast \U0001f7e5</div>', unsafe_allow_html=True)
                    st.markdown(
                        '\U0001f7e8 <b style="color:#ffd700;">' + cp_a + '</b>: ~' + str(round(y_a, 1)) + ' yellows<br>'
                        + '\U0001f7e8 <b style="color:#ffd700;">' + cp_b + '</b>: ~' + str(round(y_b, 1)) + ' yellows<br>'
                        + '\U0001f7e8 Total: ~' + str(round(total_y, 1)) + ' yellows<br>'
                        + '\U0001f7e5 Red probability: <b>' + str(round(100 * red_prob, 1)) + '%</b>',
                        unsafe_allow_html=True
                    )
                    if red_prob > 0.25:
                        st.markdown('\U0001f7e5 <b style="color:#ff3333;">HIGH red card risk! Heated match!</b>', unsafe_allow_html=True)
                    elif red_prob > 0.15:
                        st.markdown('\U0001f7e8 <b style="color:#ffd700;">Moderate red card risk.</b>', unsafe_allow_html=True)
                    else:
                        st.markdown('\U0001f7e9 <b style="color:#00ff88;">Low red card risk.</b>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error("Error: " + str(e))

    with st.expander("\U0001f5d1\ufe0f Clear Recent Data"):
        if st.button("Clear ALL recent results"):
            pd.DataFrame(columns=["date","home_team","away_team","home_score","away_score","tournament","city","country","neutral"]).to_csv("data/recent_results.csv", index=False)
            pd.DataFrame(columns=["date","home_team","away_team","team","scorer","minute","own_goal","penalty"]).to_csv("data/recent_goalscorers.csv", index=False)
            try:
                from prediction_engine import clear_cache
                clear_cache()
            except Exception:
                pass
            st.success("\U0001f5d1\ufe0f All recent data cleared!")

'''

    # Insert before the final else block
    else_marker = 'else:\n    st.markdown('
    idx = content.rfind(else_marker)
    if idx > -1:
        content = content[:idx] + admin_section + '\n' + content[idx:]
        print("  [2] Added admin panel + card predictor to sidebar")
        changes += 1

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
new = len(content.splitlines())
print("\nDone! " + str(changes) + " changes, " + str(new) + " lines")
