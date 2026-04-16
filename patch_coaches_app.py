with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# CHANGE 1: Add coaches section after Key Player Impact section
old_kp = '''    if top_scores:
        st.markdown("### 🎯 Most Likely Scorelines")'''

new_coaches_block = '''    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  COACHES MATCHUP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("### 🏆 Coaches Matchup")
    coach_a_name = result.get("team_a_coach", "Unknown")
    coach_b_name = result.get("team_b_coach", "Unknown")
    coach_a_tier = result.get("team_a_coach_tier", "N/A")
    coach_b_tier = result.get("team_b_coach_tier", "N/A")
    coach_a_style = result.get("team_a_coach_style", "N/A")
    coach_b_style = result.get("team_b_coach_style", "N/A")
    coach_a_atk = float(result.get("team_a_coach_atk", 1.0))
    coach_a_def = float(result.get("team_a_coach_def", 1.0))
    coach_b_atk = float(result.get("team_b_coach_atk", 1.0))
    coach_b_def = float(result.get("team_b_coach_def", 1.0))
    coach_a_honors = result.get("team_a_coach_honors", [])
    coach_b_honors = result.get("team_b_coach_honors", [])
    coach_a_notes = result.get("team_a_coach_notes", "")
    coach_b_notes = result.get("team_b_coach_notes", "")

    ca, cb = st.columns(2)
    with ca:
        st.markdown(f"**{da}**")
        st.markdown(f"Coach: **{coach_a_name}**")
        st.markdown(f"Tier: {coach_a_tier}")
        st.markdown(f"Style: {coach_a_style}")
        st.markdown(f"Impact: ATK x{coach_a_atk:.3f} | DEF x{coach_a_def:.3f}")
        if coach_a_honors:
            st.markdown(f"Honors: {', '.join(coach_a_honors[:3])}")
        if coach_a_notes:
            st.caption(coach_a_notes[:100])
    with cb:
        st.markdown(f"**{db}**")
        st.markdown(f"Coach: **{coach_b_name}**")
        st.markdown(f"Tier: {coach_b_tier}")
        st.markdown(f"Style: {coach_b_style}")
        st.markdown(f"Impact: ATK x{coach_b_atk:.3f} | DEF x{coach_b_def:.3f}")
        if coach_b_honors:
            st.markdown(f"Honors: {', '.join(coach_b_honors[:3])}")
        if coach_b_notes:
            st.caption(coach_b_notes[:100])

    if top_scores:
        st.markdown("### 🎯 Most Likely Scorelines")'''

if 'Coaches Matchup' not in code:
    code = code.replace(old_kp, new_coaches_block)
    print('SUCCESS: Coaches Matchup added to app.py')
else:
    print('SKIP: Coaches Matchup already exists in app.py')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
