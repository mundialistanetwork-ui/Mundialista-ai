"""
Task 06: Your First Streamlit App
==================================
"""
import streamlit as st

# ── Title ───────────────────────────────────────────────────
st.title("⚽ Mundialista Network AI")
st.subheader("My First Streamlit App")

# ── Text ────────────────────────────────────────────────────
st.write("Hello! I'm building a football prediction engine.")
st.write("This is **bold** and this is *italic*.")

# ── A simple calculation ────────────────────────────────────
goals_home = 2
goals_away = 1
st.write(f"If Jamaica scores {goals_home} and New Caledonia "
         f"scores {goals_away}, Jamaica wins!")

# ── An interactive widget ───────────────────────────────────
name = st.text_input("What's your name?", value="Football Fan")
st.write(f"Welcome to Mundialista, {name}! 🎉")

# ── A slider ────────────────────────────────────────────────
goals = st.slider("How many goals do you predict?", 
                   min_value=0, max_value=10, value=3)
st.write(f"You predicted {goals} total goals in the match.")

# ── A button ────────────────────────────────────────────────
if st.button("Click me!"):
    st.balloons()
    st.success("You pressed the button! 🎊")

# ── Sidebar ─────────────────────────────────────────────────
st.sidebar.header("Settings")
st.sidebar.write("This is the sidebar. We'll put team "
                 "selection here later.")