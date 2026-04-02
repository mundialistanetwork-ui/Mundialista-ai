# Mundialista AI App Builder
import os

lines = []
def L(s):
    lines.append(s)

# === IMPORTS ===
L("import matplotlib")
L("matplotlib.use('Agg')")
L("")
L("import streamlit as st")
L("import pandas as pd")
L("import os")
L("")
L("from prediction_engine import predict, load_rankings")
L("from chart_generator import generate_all_charts")
L("")
L('st.set_page_config(')
L('    page_title="Mundialista AI",')
L('    page_icon="\u26bd",')
L('    layout="wide",')
L('    initial_sidebar_state="collapsed"')
L(')')
L("")
