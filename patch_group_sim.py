with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add imports at the top
if 'from content_automation import WC2026_GROUPS' not in code:
    code = code.replace(
        'from prediction_engine import predict, get_all_teams, get_team_ranking, clean_match_type',
        'from prediction_engine import predict, get_all_teams, get_team_ranking, clean_match_type\nfrom content_automation import WC2026_GROUPS, resolve_team_name, display_name'
    )

# Add the group simulator section before the underdog spotlight
old_underdog = '''st.markdown("---")
render_underdog_spotlight()'''

new_group_sim = '''st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  WC 2026 GROUP STAGE SIMULATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("## 🏆 World Cup 2026 — Group Stage Simulator")
st.caption("48 teams • 12 groups • Dixon-Coles Poisson engine • 10,200 simulations per match")

group_tab_labels = [f"Group {g}" for g in sorted(WC2026_GROUPS.keys())]
group_tabs = st.tabs(group_tab_labels)

for tab, group_letter in zip(group_tabs, sorted(WC2026_GROUPS.keys())):
    with tab:
        display_teams = WC2026_GROUPS[group_letter]
        data_teams = [resolve_team_name(t) for t in display_teams]

        st.markdown(f"### Group {group_letter}")
        st.markdown(f"**Teams:** {' • '.join(display_teams)}")

        run_group = st.button(f"⚽ Simulate Group {group_letter}", key=f"group_{group_letter}")

        session_key = f"group_result_{group_letter}"

        if run_group:
            points = {t: 0.0 for t in display_teams}
            gd = {t: 0.0 for t in display_teams}
            gf_tot = {t: 0.0 for t in display_teams}
            ga_tot = {t: 0.0 for t in display_teams}
            match_results = []

            progress = st.progress(0)
            total_matches = len(display_teams) * (len(display_teams) - 1) // 2
            match_count = 0

            for i in range(len(display_teams)):
                for j in range(i + 1, len(display_teams)):
                    h_display = display_teams[i]
                    a_display = display_teams[j]
                    h_data = data_teams[i]
                    a_data = data_teams[j]

                    try:
                        result_match = predict(h_data, a_data, home=None)
                    except Exception as e:
                        st.warning(f"Could not predict {h_display} vs {a_display}: {e}")
                        match_count += 1
                        progress.progress(match_count / total_matches)
                        continue

                    hw = float(result_match.get("team_a_win", 33.3))
                    dr = float(result_match.get("draw", 33.4))
                    aw = float(result_match.get("team_b_win", 33.3))
                    hxg = float(result_match.get("team_a_lambda", 1.0))
                    axg = float(result_match.get("team_b_lambda", 1.0))

                    # Coaches data
                    h_coach = result_match.get("team_a_coach", "Unknown")
                    a_coach = result_match.get("team_b_coach", "Unknown")
                    h_coach_tier = result_match.get("team_a_coach_tier", "N/A")
                    a_coach_tier = result_match.get("team_b_coach_tier", "N/A")

                    top_scores = result_match.get("top_scores", [])
                    top_score_str = str(top_scores[0][0]) if top_scores else "N/A"
                    top_score_pct = top_scores[0][1] if top_scores else 0

                    hw_frac = hw / 100
                    dr_frac = dr / 100
                    aw_frac = aw / 100

                    points[h_display] += hw_frac * 3 + dr_frac * 1
                    points[a_display] += aw_frac * 3 + dr_frac * 1
                    gd[h_display] += hxg - axg
                    gd[a_display] += axg - hxg
                    gf_tot[h_display] += hxg
                    gf_tot[a_display] += axg
                    ga_tot[h_display] += axg
                    ga_tot[a_display] += hxg

                    match_results.append({
                        "home": h_display,
                        "away": a_display,
                        "home_win": hw,
                        "draw": dr,
                        "away_win": aw,
                        "home_xg": hxg,
                        "away_xg": axg,
                        "top_score": top_score_str,
                        "top_score_pct": top_score_pct,
                        "home_coach": h_coach,
                        "away_coach": a_coach,
                        "home_coach_tier": h_coach_tier,
                        "away_coach_tier": a_coach_tier,
                    })

                    match_count += 1
                    progress.progress(match_count / total_matches)

            progress.empty()

            standings = sorted(
                display_teams,
                key=lambda t: (points[t], gd[t], gf_tot[t]),
                reverse=True,
            )

            st.session_state[session_key] = {
                "standings": standings,
                "points": points,
                "gd": gd,
                "gf": gf_tot,
                "ga": ga_tot,
                "matches": match_results,
            }

        if session_key in st.session_state:
            data = st.session_state[session_key]
            standings = data["standings"]
            pts = data["points"]
            gd_d = data["gd"]
            gf_d = data["gf"]
            ga_d = data["ga"]
            matches = data["matches"]

            st.markdown("#### 📊 Predicted Standings")

            import pandas as _pd_inner
            rows = []
            for rank, t in enumerate(standings, 1):
                if rank <= 2:
                    status = "✅ Qualify"
                elif rank == 3:
                    status = "🟡 Possible 3rd"
                else:
                    status = "❌ Eliminated"
                rows.append({
                    "Pos": rank,
                    "Team": t,
                    "Pts": round(pts[t], 1),
                    "GD": f"{gd_d[t]:+.2f}",
                    "GF": round(gf_d[t], 2),
                    "GA": round(ga_d[t], 2),
                    "Status": status,
                })

            df_standings = _pd_inner.DataFrame(rows)
            st.dataframe(df_standings, use_container_width=True, hide_index=True)

            st.markdown("#### ⚽ Match-by-Match Breakdown")

            for m in matches:
                with st.expander(f"{m['home']} vs {m['away']} — xG: {m['home_xg']:.2f} vs {m['away_xg']:.2f}"):
                    mc1, mc2, mc3 = st.columns(3)
                    with mc1:
                        st.metric(f"{m['home']} Win", f"{m['home_win']:.1f}%")
                    with mc2:
                        st.metric("Draw", f"{m['draw']:.1f}%")
                    with mc3:
                        st.metric(f"{m['away']} Win", f"{m['away_win']:.1f}%")

                    st.markdown(f"**Most likely score:** {m['top_score']} ({m['top_score_pct']:.1f}%)")

                    st.markdown("**Coaches:**")
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        st.markdown(f"{m['home']}: **{m['home_coach']}** ({m['home_coach_tier']})")
                    with cc2:
                        st.markdown(f"{m['away']}: **{m['away_coach']}** ({m['away_coach_tier']})")

            st.markdown("#### 🏆 Qualification Summary")
            q1, q2 = st.columns(2)
            with q1:
                st.success(f"**Auto-qualify:** {standings[0]} ({pts[standings[0]]:.1f} pts)")
            with q2:
                st.success(f"**Auto-qualify:** {standings[1]} ({pts[standings[1]]:.1f} pts)")
            st.warning(f"**Best 3rd chance:** {standings[2]} ({pts[standings[2]]:.1f} pts)")
            st.error(f"**Eliminated:** {standings[3]} ({pts[standings[3]]:.1f} pts)")

st.markdown("---")
render_underdog_spotlight()'''

if 'Group Stage Simulator' not in code:
    code = code.replace(old_underdog, new_group_sim)
    print('SUCCESS: WC 2026 Group Stage Simulator added to app.py')
else:
    print('SKIP: Group Stage Simulator already exists in app.py')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
