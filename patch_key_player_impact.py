from pathlib import Path

path = Path("app.py")
text = path.read_text(encoding="utf-8")

# Add helper if missing
if "def format_key_players(" not in text:
    marker = "def build_simple_insight("
    idx = text.find(marker)
    if idx == -1:
        raise SystemExit("Could not find build_simple_insight() marker.")

    helper = '''
def format_key_players(players):
    lines = []
    for p in players[:5]:
        if isinstance(p, dict):
            name = p.get("name", "Unknown")
            tier = p.get("tier_label") or p.get("tier") or ""
            role = p.get("role", "")
            details = []
            if tier:
                details.append(str(tier).title())
            if role:
                details.append(str(role).title())
            if details:
                lines.append(f"- {name} ({', '.join(details)})")
            else:
                lines.append(f"- {name}")
        else:
            lines.append(f"- {p}")
    return lines

'''
    text = text[:idx] + helper + text[idx:]

# Rename section title
text = text.replace(
    'st.markdown("### 🌟 Star Player Impact")',
    'st.markdown("### 🌟 Key Player Impact")'
)

# Replace list rendering block
old = '''    st.markdown("### 🌟 Star Player Impact")
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
            st.caption("No star player data")'''

new = '''    st.markdown("### 🌟 Key Player Impact")
    sa, sb = st.columns(2)
    with sa:
        st.markdown(f"**{da}** — ATK x{boost_a:.2f} | DEF x{def_a:.2f}")
        if stars_a:
            for line in format_key_players(stars_a):
                st.markdown(line)
        else:
            st.caption("No key player data")
    with sb:
        st.markdown(f"**{db}** — ATK x{boost_b:.2f} | DEF x{def_b:.2f}")
        if stars_b:
            for line in format_key_players(stars_b):
                st.markdown(line)
        else:
            st.caption("No key player data")'''

if old not in text:
    raise SystemExit("Could not find Key/Star player display block.")

text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

print("Updated UI to Key Player Impact with tier-aware display.")
