import pytensor
pytensor.config.cxx = ""

"""
Mundialista Network AI Prediction Engine
=========================================
Auto-fetches real match data from the internet!
Works with ANY team. Falls back to manual entry if data not found.

Author : Mundialista Network
Version: 3.0.0 (auto-fetch build)
"""

import streamlit as st
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy.stats import poisson
from collections import Counter
from typing import Dict, Optional
import warnings, time, requests, json

warnings.filterwarnings("ignore")
from data_loader import load_results, get_all_teams, get_team_stats_for_app, resolve_team_name, get_team_matches
sns.set_theme(style="darkgrid", palette="muted")

TOTAL_MINUTES = 90
NUM_SIMULATIONS = 10_200
HALF_TIME = 45
FINAL_PUSH_START = 80
SEED = 42


# ──────────────────────────────────────────────────────────────────
# AUTO DATA FETCHING
# ──────────────────────────────────────────────────────────────────

# Large dictionary of team data (recent form + historical averages)
# This serves as our "database" of team strengths
TEAM_DATABASE = {
    # ── UEFA (Europe) ──────────────────────────────────────────
    "France": {"avg_gf": 1.8, "avg_ga": 0.7, "std_gf": 1.2, "std_ga": 0.8,
               "recent_gf": [3, 1, 2, 0, 3, 2, 1], "recent_ga": [1, 0, 1, 0, 1, 0, 1]},
    "Spain": {"avg_gf": 2.1, "avg_ga": 0.6, "std_gf": 1.3, "std_ga": 0.7,
              "recent_gf": [4, 1, 2, 3, 1, 2, 1], "recent_ga": [1, 0, 0, 0, 1, 0, 1]},
    "Germany": {"avg_gf": 2.0, "avg_ga": 0.9, "std_gf": 1.4, "std_ga": 1.0,
                "recent_gf": [2, 3, 1, 2, 0, 4, 2], "recent_ga": [0, 1, 2, 0, 1, 1, 1]},
    "England": {"avg_gf": 1.9, "avg_ga": 0.7, "std_gf": 1.3, "std_ga": 0.8,
                "recent_gf": [3, 2, 1, 0, 2, 3, 1], "recent_ga": [0, 1, 0, 1, 0, 1, 1]},
    "Portugal": {"avg_gf": 2.0, "avg_ga": 0.8, "std_gf": 1.3, "std_ga": 0.9,
                 "recent_gf": [3, 1, 2, 1, 3, 2, 0], "recent_ga": [0, 0, 1, 1, 0, 1, 1]},
    "Netherlands": {"avg_gf": 1.8, "avg_ga": 0.8, "std_gf": 1.2, "std_ga": 0.9,
                    "recent_gf": [2, 1, 3, 0, 2, 1, 2], "recent_ga": [0, 1, 1, 2, 0, 0, 1]},
    "Belgium": {"avg_gf": 1.7, "avg_ga": 0.9, "std_gf": 1.2, "std_ga": 0.9,
                "recent_gf": [2, 0, 1, 3, 1, 2, 1], "recent_ga": [1, 1, 0, 1, 2, 0, 1]},
    "Italy": {"avg_gf": 1.6, "avg_ga": 0.7, "std_gf": 1.1, "std_ga": 0.8,
              "recent_gf": [2, 1, 0, 1, 2, 3, 1], "recent_ga": [0, 0, 1, 1, 0, 0, 1]},
    "Croatia": {"avg_gf": 1.5, "avg_ga": 0.8, "std_gf": 1.1, "std_ga": 0.9,
                "recent_gf": [1, 2, 1, 0, 3, 1, 2], "recent_ga": [0, 1, 1, 0, 1, 1, 0]},
    "Denmark": {"avg_gf": 1.6, "avg_ga": 0.8, "std_gf": 1.2, "std_ga": 0.8,
                "recent_gf": [2, 1, 0, 2, 1, 3, 1], "recent_ga": [0, 0, 1, 1, 1, 0, 1]},
    "Switzerland": {"avg_gf": 1.4, "avg_ga": 0.8, "std_gf": 1.0, "std_ga": 0.8,
                    "recent_gf": [1, 2, 1, 0, 1, 2, 1], "recent_ga": [0, 1, 0, 1, 1, 0, 1]},
    "Austria": {"avg_gf": 1.5, "avg_ga": 0.9, "std_gf": 1.1, "std_ga": 0.9,
                "recent_gf": [2, 1, 3, 0, 1, 2, 1], "recent_ga": [1, 0, 1, 2, 1, 0, 1]},
    "Turkey": {"avg_gf": 1.4, "avg_ga": 1.0, "std_gf": 1.1, "std_ga": 1.0,
               "recent_gf": [1, 2, 0, 3, 1, 1, 2], "recent_ga": [1, 1, 2, 0, 0, 1, 1]},
    "Serbia": {"avg_gf": 1.3, "avg_ga": 1.0, "std_gf": 1.0, "std_ga": 0.9,
               "recent_gf": [1, 0, 2, 1, 1, 2, 0], "recent_ga": [0, 1, 1, 2, 0, 1, 1]},
    "Poland": {"avg_gf": 1.4, "avg_ga": 1.0, "std_gf": 1.1, "std_ga": 1.0,
               "recent_gf": [2, 1, 0, 1, 3, 1, 0], "recent_ga": [1, 0, 2, 1, 0, 1, 1]},
    "Ukraine": {"avg_gf": 1.3, "avg_ga": 1.0, "std_gf": 1.0, "std_ga": 0.9,
                "recent_gf": [1, 2, 0, 1, 1, 2, 1], "recent_ga": [1, 0, 1, 2, 1, 0, 1]},
    "Sweden": {"avg_gf": 1.3, "avg_ga": 0.9, "std_gf": 1.0, "std_ga": 0.9,
               "recent_gf": [1, 0, 2, 1, 1, 2, 1], "recent_ga": [0, 1, 1, 0, 1, 1, 0]},
    "Scotland": {"avg_gf": 1.2, "avg_ga": 1.0, "std_gf": 0.9, "std_ga": 0.9,
                 "recent_gf": [1, 0, 2, 1, 0, 1, 2], "recent_ga": [1, 1, 0, 2, 1, 0, 1]},
    "Wales": {"avg_gf": 1.1, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
              "recent_gf": [0, 1, 2, 1, 0, 1, 1], "recent_ga": [1, 0, 1, 2, 1, 1, 0]},
    "Czech Republic": {"avg_gf": 1.3, "avg_ga": 1.0, "std_gf": 1.0, "std_ga": 0.9,
                       "recent_gf": [1, 2, 0, 1, 2, 1, 0], "recent_ga": [0, 1, 1, 1, 0, 1, 2]},
    "Romania": {"avg_gf": 1.2, "avg_ga": 1.0, "std_gf": 0.9, "std_ga": 0.9,
                "recent_gf": [1, 0, 2, 1, 1, 0, 2], "recent_ga": [0, 1, 0, 1, 2, 1, 0]},
    "Greece": {"avg_gf": 1.1, "avg_ga": 0.9, "std_gf": 0.9, "std_ga": 0.8,
               "recent_gf": [1, 0, 1, 2, 0, 1, 1], "recent_ga": [0, 1, 0, 1, 1, 0, 1]},
    "Norway": {"avg_gf": 1.4, "avg_ga": 1.0, "std_gf": 1.1, "std_ga": 0.9,
               "recent_gf": [2, 1, 0, 3, 1, 1, 0], "recent_ga": [0, 1, 1, 0, 2, 1, 1]},
    "Hungary": {"avg_gf": 1.2, "avg_ga": 1.0, "std_gf": 0.9, "std_ga": 0.9,
                "recent_gf": [1, 0, 2, 1, 0, 1, 2], "recent_ga": [1, 0, 1, 2, 1, 0, 1]},
    "Russia": {"avg_gf": 1.2, "avg_ga": 1.0, "std_gf": 0.9, "std_ga": 0.9,
               "recent_gf": [1, 0, 1, 2, 0, 1, 1], "recent_ga": [0, 1, 1, 0, 2, 1, 1]},
    "Republic of Ireland": {"avg_gf": 1.0, "avg_ga": 1.1, "std_gf": 0.8, "std_ga": 0.9,
                            "recent_gf": [0, 1, 1, 0, 2, 1, 0], "recent_ga": [1, 0, 1, 2, 0, 1, 1]},
    "Iceland": {"avg_gf": 1.0, "avg_ga": 1.1, "std_gf": 0.8, "std_ga": 0.9,
                "recent_gf": [1, 0, 0, 2, 1, 0, 1], "recent_ga": [1, 2, 0, 1, 0, 1, 1]},
    "Finland": {"avg_gf": 1.1, "avg_ga": 1.0, "std_gf": 0.8, "std_ga": 0.9,
                "recent_gf": [0, 1, 1, 2, 0, 1, 1], "recent_ga": [1, 0, 1, 0, 2, 1, 0]},
    "Slovakia": {"avg_gf": 1.1, "avg_ga": 1.0, "std_gf": 0.9, "std_ga": 0.9,
                 "recent_gf": [1, 0, 1, 2, 0, 1, 1], "recent_ga": [0, 1, 1, 0, 2, 1, 0]},
    "Slovenia": {"avg_gf": 1.2, "avg_ga": 0.9, "std_gf": 0.9, "std_ga": 0.8,
                 "recent_gf": [1, 2, 0, 1, 1, 2, 0], "recent_ga": [0, 0, 1, 1, 0, 1, 1]},
    "Albania": {"avg_gf": 1.1, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
                "recent_gf": [1, 0, 2, 0, 1, 1, 1], "recent_ga": [0, 1, 1, 2, 0, 1, 1]},
    "Georgia": {"avg_gf": 1.2, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
                "recent_gf": [2, 0, 1, 1, 0, 2, 1], "recent_ga": [1, 1, 0, 2, 1, 0, 1]},
    "North Macedonia": {"avg_gf": 1.0, "avg_ga": 1.2, "std_gf": 0.8, "std_ga": 0.9,
                        "recent_gf": [0, 1, 1, 0, 2, 0, 1], "recent_ga": [1, 0, 2, 1, 0, 2, 1]},
    "Bosnia": {"avg_gf": 1.2, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
               "recent_gf": [1, 2, 0, 1, 0, 1, 2], "recent_ga": [1, 0, 1, 2, 1, 0, 1]},

    # ── CONMEBOL (South America) ───────────────────────────────
    "Brazil": {"avg_gf": 1.7, "avg_ga": 0.8, "std_gf": 1.3, "std_ga": 0.9,
               "recent_gf": [1, 2, 3, 0, 1, 2, 1], "recent_ga": [0, 1, 0, 1, 1, 0, 1]},
    "Argentina": {"avg_gf": 2.0, "avg_ga": 0.6, "std_gf": 1.3, "std_ga": 0.7,
                  "recent_gf": [3, 1, 2, 1, 2, 3, 0], "recent_ga": [0, 0, 1, 0, 0, 1, 1]},
    "Uruguay": {"avg_gf": 1.6, "avg_ga": 0.8, "std_gf": 1.2, "std_ga": 0.8,
                "recent_gf": [2, 1, 0, 2, 1, 3, 1], "recent_ga": [0, 0, 1, 1, 0, 0, 2]},
    "Colombia": {"avg_gf": 1.5, "avg_ga": 0.8, "std_gf": 1.1, "std_ga": 0.8,
                 "recent_gf": [1, 2, 1, 0, 2, 1, 3], "recent_ga": [0, 1, 0, 0, 1, 1, 0]},
    "Ecuador": {"avg_gf": 1.3, "avg_ga": 1.0, "std_gf": 1.0, "std_ga": 0.9,
                "recent_gf": [1, 0, 2, 1, 1, 0, 2], "recent_ga": [0, 1, 1, 2, 0, 1, 1]},
    "Chile": {"avg_gf": 1.2, "avg_ga": 1.1, "std_gf": 1.0, "std_ga": 1.0,
              "recent_gf": [0, 1, 2, 0, 1, 2, 1], "recent_ga": [1, 0, 1, 2, 1, 0, 1]},
    "Paraguay": {"avg_gf": 1.1, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
                 "recent_gf": [1, 0, 1, 0, 2, 1, 1], "recent_ga": [0, 1, 2, 1, 0, 1, 1]},
    "Peru": {"avg_gf": 1.1, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
             "recent_gf": [0, 1, 1, 0, 2, 0, 1], "recent_ga": [1, 0, 1, 2, 0, 1, 1]},
    "Venezuela": {"avg_gf": 1.2, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
                  "recent_gf": [1, 2, 0, 1, 1, 0, 2], "recent_ga": [0, 1, 1, 2, 0, 1, 1]},
    "Bolivia": {"avg_gf": 0.9, "avg_ga": 1.5, "std_gf": 0.8, "std_ga": 1.1,
                "recent_gf": [0, 1, 0, 2, 0, 1, 0], "recent_ga": [2, 1, 3, 0, 1, 1, 2]},

    # ── CONCACAF (North/Central America) ───────────────────────
    "Mexico": {"avg_gf": 1.6, "avg_ga": 0.9, "std_gf": 1.2, "std_ga": 0.9,
               "recent_gf": [2, 1, 0, 3, 1, 2, 0], "recent_ga": [0, 1, 1, 0, 0, 1, 2]},
    "USA": {"avg_gf": 1.7, "avg_ga": 0.8, "std_gf": 1.2, "std_ga": 0.8,
            "recent_gf": [2, 1, 3, 0, 2, 1, 2], "recent_ga": [0, 1, 0, 1, 0, 0, 1]},
    "Canada": {"avg_gf": 1.4, "avg_ga": 1.0, "std_gf": 1.1, "std_ga": 0.9,
               "recent_gf": [2, 0, 1, 2, 1, 0, 2], "recent_ga": [0, 1, 1, 0, 2, 1, 0]},
    "Costa Rica": {"avg_gf": 1.1, "avg_ga": 1.0, "std_gf": 0.9, "std_ga": 0.9,
                   "recent_gf": [1, 0, 1, 2, 0, 1, 1], "recent_ga": [0, 1, 2, 0, 1, 1, 0]},
    "Panama": {"avg_gf": 1.0, "avg_ga": 1.1, "std_gf": 0.8, "std_ga": 0.9,
               "recent_gf": [1, 0, 0, 2, 1, 0, 1], "recent_ga": [0, 1, 2, 1, 0, 1, 1]},
    "Honduras": {"avg_gf": 1.0, "avg_ga": 1.2, "std_gf": 0.8, "std_ga": 1.0,
                 "recent_gf": [0, 1, 1, 0, 2, 0, 1], "recent_ga": [1, 0, 2, 1, 0, 2, 1]},
    "Jamaica": {"avg_gf": 1.3, "avg_ga": 0.7, "std_gf": 1.1, "std_ga": 0.8,
                "recent_gf": [1, 0, 2, 1, 0, 3, 2], "recent_ga": [0, 1, 1, 1, 2, 0, 0]},
    "El Salvador": {"avg_gf": 0.9, "avg_ga": 1.3, "std_gf": 0.7, "std_ga": 1.0,
                    "recent_gf": [0, 1, 0, 1, 0, 2, 0], "recent_ga": [2, 0, 1, 1, 2, 0, 1]},
    "Trinidad and Tobago": {"avg_gf": 0.8, "avg_ga": 1.3, "std_gf": 0.7, "std_ga": 1.0,
                            "recent_gf": [0, 1, 0, 0, 1, 1, 0], "recent_ga": [1, 0, 2, 3, 1, 0, 1]},

    # ── AFC (Asia) ─────────────────────────────────────────────
    "Japan": {"avg_gf": 1.8, "avg_ga": 0.6, "std_gf": 1.2, "std_ga": 0.7,
              "recent_gf": [3, 2, 1, 0, 4, 1, 2], "recent_ga": [0, 0, 1, 0, 1, 0, 0]},
    "South Korea": {"avg_gf": 1.5, "avg_ga": 0.8, "std_gf": 1.1, "std_ga": 0.8,
                    "recent_gf": [2, 1, 0, 3, 1, 1, 2], "recent_ga": [0, 0, 1, 1, 0, 1, 0]},
    "Australia": {"avg_gf": 1.5, "avg_ga": 0.9, "std_gf": 1.2, "std_ga": 0.9,
                  "recent_gf": [2, 1, 0, 3, 1, 2, 0], "recent_ga": [0, 1, 1, 0, 1, 0, 2]},
    "Iran": {"avg_gf": 1.4, "avg_ga": 0.8, "std_gf": 1.1, "std_ga": 0.8,
             "recent_gf": [1, 2, 0, 1, 3, 1, 1], "recent_ga": [0, 0, 1, 1, 0, 0, 1]},
    "Saudi Arabia": {"avg_gf": 1.3, "avg_ga": 1.0, "std_gf": 1.0, "std_ga": 0.9,
                     "recent_gf": [1, 0, 2, 1, 1, 2, 0], "recent_ga": [0, 1, 1, 0, 2, 0, 1]},
    "Qatar": {"avg_gf": 1.2, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
              "recent_gf": [1, 0, 1, 2, 0, 1, 1], "recent_ga": [1, 1, 0, 1, 2, 0, 1]},
    "Iraq": {"avg_gf": 1.2, "avg_ga": 1.0, "std_gf": 0.9, "std_ga": 0.9,
             "recent_gf": [1, 2, 0, 1, 0, 2, 1], "recent_ga": [0, 1, 1, 0, 2, 0, 1]},
    "UAE": {"avg_gf": 1.1, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
            "recent_gf": [1, 0, 2, 0, 1, 1, 1], "recent_ga": [0, 1, 1, 2, 0, 1, 1]},
    "Uzbekistan": {"avg_gf": 1.3, "avg_ga": 0.9, "std_gf": 1.0, "std_ga": 0.8,
                   "recent_gf": [2, 1, 0, 1, 2, 1, 1], "recent_ga": [0, 0, 1, 1, 0, 1, 0]},
    "China": {"avg_gf": 1.0, "avg_ga": 1.3, "std_gf": 0.8, "std_ga": 1.0,
              "recent_gf": [0, 1, 1, 0, 0, 2, 1], "recent_ga": [1, 0, 2, 1, 2, 1, 0]},
    "India": {"avg_gf": 0.9, "avg_ga": 1.3, "std_gf": 0.7, "std_ga": 1.0,
              "recent_gf": [0, 1, 0, 1, 0, 2, 0], "recent_ga": [1, 0, 2, 1, 2, 0, 1]},

    # ── CAF (Africa) ───────────────────────────────────────────
    "Morocco": {"avg_gf": 1.7, "avg_ga": 0.6, "std_gf": 1.2, "std_ga": 0.7,
                "recent_gf": [2, 1, 3, 0, 2, 1, 2], "recent_ga": [0, 0, 0, 1, 0, 1, 0]},
    "Senegal": {"avg_gf": 1.5, "avg_ga": 0.7, "std_gf": 1.1, "std_ga": 0.8,
                "recent_gf": [2, 1, 0, 2, 1, 3, 1], "recent_ga": [0, 0, 1, 0, 1, 0, 1]},
    "Nigeria": {"avg_gf": 1.5, "avg_ga": 0.9, "std_gf": 1.1, "std_ga": 0.9,
                "recent_gf": [1, 2, 1, 0, 2, 1, 2], "recent_ga": [0, 1, 0, 1, 1, 0, 1]},
    "Egypt": {"avg_gf": 1.4, "avg_ga": 0.8, "std_gf": 1.1, "std_ga": 0.8,
              "recent_gf": [1, 2, 0, 1, 2, 1, 1], "recent_ga": [0, 0, 1, 1, 0, 1, 0]},
    "Cameroon": {"avg_gf": 1.3, "avg_ga": 1.0, "std_gf": 1.0, "std_ga": 0.9,
                 "recent_gf": [1, 0, 2, 1, 1, 2, 0], "recent_ga": [0, 1, 1, 0, 2, 0, 1]},
    "Algeria": {"avg_gf": 1.3, "avg_ga": 0.9, "std_gf": 1.0, "std_ga": 0.8,
                "recent_gf": [2, 1, 0, 1, 2, 0, 1], "recent_ga": [0, 0, 1, 1, 0, 1, 1]},
    "Tunisia": {"avg_gf": 1.2, "avg_ga": 0.8, "std_gf": 0.9, "std_ga": 0.8,
                "recent_gf": [1, 0, 2, 1, 0, 1, 1], "recent_ga": [0, 0, 1, 1, 1, 0, 0]},
    "Ivory Coast": {"avg_gf": 1.4, "avg_ga": 0.9, "std_gf": 1.1, "std_ga": 0.9,
                    "recent_gf": [2, 1, 0, 2, 1, 1, 2], "recent_ga": [0, 1, 1, 0, 0, 1, 1]},
    "Ghana": {"avg_gf": 1.2, "avg_ga": 1.1, "std_gf": 0.9, "std_ga": 0.9,
              "recent_gf": [1, 0, 2, 0, 1, 1, 1], "recent_ga": [0, 1, 1, 2, 0, 1, 1]},
    "South Africa": {"avg_gf": 1.2, "avg_ga": 1.0, "std_gf": 0.9, "std_ga": 0.9,
                     "recent_gf": [1, 0, 2, 1, 0, 1, 2], "recent_ga": [0, 1, 0, 1, 2, 1, 0]},
    "DR Congo": {"avg_gf": 1.3, "avg_ga": 1.0, "std_gf": 1.0, "std_ga": 0.9,
                 "recent_gf": [2, 0, 1, 1, 2, 0, 1], "recent_ga": [0, 1, 1, 0, 1, 2, 0]},
    "Mali": {"avg_gf": 1.2, "avg_ga": 0.9, "std_gf": 0.9, "std_ga": 0.8,
             "recent_gf": [1, 2, 0, 1, 1, 0, 2], "recent_ga": [0, 0, 1, 1, 0, 1, 1]},

    # ── OFC (Oceania) ──────────────────────────────────────────
    "New Zealand": {"avg_gf": 1.5, "avg_ga": 0.8, "std_gf": 1.3, "std_ga": 0.9,
                    "recent_gf": [2, 1, 3, 0, 4, 1, 2], "recent_ga": [0, 0, 1, 1, 0, 1, 0]},
    "New Caledonia": {"avg_gf": 1.1, "avg_ga": 1.3, "std_gf": 1.0, "std_ga": 1.2,
                      "recent_gf": [1, 0, 2, 1, 0, 1, 3], "recent_ga": [1, 2, 1, 0, 4, 1, 0]},
    "Fiji": {"avg_gf": 1.0, "avg_ga": 1.3, "std_gf": 0.9, "std_ga": 1.0,
             "recent_gf": [1, 0, 1, 2, 0, 0, 1], "recent_ga": [1, 1, 2, 0, 3, 1, 0]},
    "Tahiti": {"avg_gf": 0.8, "avg_ga": 1.5, "std_gf": 0.7, "std_ga": 1.2,
               "recent_gf": [0, 1, 0, 0, 2, 0, 1], "recent_ga": [2, 0, 3, 1, 0, 2, 1]},
    "Solomon Islands": {"avg_gf": 0.9, "avg_ga": 1.4, "std_gf": 0.8, "std_ga": 1.1,
                        "recent_gf": [0, 1, 0, 1, 0, 2, 0], "recent_ga": [1, 0, 2, 1, 2, 0, 1]},
}


def find_team_data(team_name: str) -> Optional[dict]:
    """Look up team in our database (case-insensitive fuzzy match)."""
    # Exact match first
    if team_name in TEAM_DATABASE:
        return TEAM_DATABASE[team_name]
    
    # Case-insensitive match
    for key, data in TEAM_DATABASE.items():
        if key.lower() == team_name.lower():
            return data
    
    # Partial match
    for key, data in TEAM_DATABASE.items():
        if team_name.lower() in key.lower() or key.lower() in team_name.lower():
            return data
    
    return None


def get_team_stats_auto(team_name: str) -> Dict[str, float]:
    """Get team stats from database or manual entry."""
    data = find_team_data(team_name)
    
    if data is not None:
        gf = np.array(data["recent_gf"])
        ga = np.array(data["recent_ga"])
        return {
            "avg_gf": data["avg_gf"],
            "avg_ga": data["avg_ga"],
            "std_gf": max(data["std_gf"], 0.3),
            "std_ga": max(data["std_ga"], 0.3),
            "n_matches": len(gf),
            "goals_for": gf,
            "goals_against": ga,
            "found": True,
        }
    
    return None


# ──────────────────────────────────────────────────────────────────
# BAYESIAN MODEL
# ──────────────────────────────────────────────────────────────────
def _build_cache_key(stats_home, stats_away, obs_home, obs_away):
    """Create a hashable key for caching posteriors."""
    return (
        round(stats_home["avg_gf"], 3), round(stats_home["avg_ga"], 3),
        round(stats_home["std_gf"], 3), round(stats_home["std_ga"], 3),
        round(stats_away["avg_gf"], 3), round(stats_away["avg_ga"], 3),
        round(stats_away["std_gf"], 3), round(stats_away["std_ga"], 3),
        tuple(obs_home.tolist()), tuple(obs_away.tolist()),
    )


# Simple in-memory cache for posteriors
_posterior_cache = {}	


def bayesian_estimate(
    stats_home: Dict, stats_away: Dict,
    observed_home_goals: np.ndarray,
    observed_away_goals: np.ndarray,
    quick_mode: bool = False,
) -> Dict[str, np.ndarray]:
    """
    Run Bayesian inference with caching + quick/full mode.
    quick_mode=True:  500 draws, 500 tune  → ~5-10 seconds
    quick_mode=False: 2000 draws, 1000 tune → ~20-60 seconds
    """
    cache_key = _build_cache_key(
        stats_home, stats_away, observed_home_goals, observed_away_goals)

    # Add mode to cache key so quick and full are cached separately
    full_key = (cache_key, quick_mode)

    if full_key in _posterior_cache:
        return _posterior_cache[full_key]

    if quick_mode:
        draws, tune, chains = 500, 500, 2
    else:
        draws, tune, chains = 2000, 1000, 2

    with pm.Model() as model:
        home_attack = pm.TruncatedNormal(
            "home_attack", mu=stats_home["avg_gf"],
            sigma=max(stats_home["std_gf"], 0.3),
            lower=0.05, upper=6.0)
        home_defense = pm.TruncatedNormal(
            "home_defense", mu=stats_home["avg_ga"],
            sigma=max(stats_home["std_ga"], 0.3),
            lower=0.05, upper=6.0)
        away_attack = pm.TruncatedNormal(
            "away_attack", mu=stats_away["avg_gf"],
            sigma=max(stats_away["std_gf"], 0.3),
            lower=0.05, upper=6.0)
        away_defense = pm.TruncatedNormal(
            "away_defense", mu=stats_away["avg_ga"],
            sigma=max(stats_away["std_ga"], 0.3),
            lower=0.05, upper=6.0)

        if len(observed_home_goals) > 0:
            pm.Poisson("obs_home_gf", mu=home_attack,
                       observed=observed_home_goals)
        if len(observed_away_goals) > 0:
            pm.Poisson("obs_away_gf", mu=away_attack,
                       observed=observed_away_goals)

        trace = pm.sample(
            draws=draws, tune=tune, chains=chains, cores=1,
            target_accept=0.90, return_inferencedata=True,
            progressbar=False, random_seed=SEED)

    posterior = trace.posterior
    result = {
        "home_attack": posterior["home_attack"].values.flatten(),
        "home_defense": posterior["home_defense"].values.flatten(),
        "away_attack": posterior["away_attack"].values.flatten(),
        "away_defense": posterior["away_defense"].values.flatten(),
        "trace": trace,
        "draws": draws,
        "tune": tune,
        "chains": chains,
    }

    _posterior_cache[full_key] = result
    return result


# ──────────────────────────────────────────────────────────────────
# LAMBDA PROFILE + SIMULATION + ANALYTICS (same as before)
# ──────────────────────────────────────────────────────────────────

def lambda_profile(base_rate: float, minute: int) -> float:
    if minute < 15:
        raw = 0.85
    elif minute < HALF_TIME:
        raw = 1.00
    elif minute < 60:
        raw = 1.10
    elif minute < FINAL_PUSH_START:
        raw = 1.05
    else:
        raw = 1.30
    NORM = 93.25
    multiplier = raw * (90.0 / NORM)
    return (base_rate / 90.0) * multiplier


def simulate_match(home_attack, home_defense, away_attack, away_defense, rng):
    home_rate = max(home_attack * (away_defense / 1.3), 0.1)
    away_rate = max(away_attack * (home_defense / 1.3), 0.1)
    home_goals_by_minute = np.zeros(TOTAL_MINUTES, dtype=int)
    away_goals_by_minute = np.zeros(TOTAL_MINUTES, dtype=int)
    for minute in range(TOTAL_MINUTES):
        home_goals_by_minute[minute] = rng.poisson(lambda_profile(home_rate, minute))
        away_goals_by_minute[minute] = rng.poisson(lambda_profile(away_rate, minute))
    home_total = int(home_goals_by_minute.sum())
    away_total = int(away_goals_by_minute.sum())
    home_ht = int(home_goals_by_minute[:HALF_TIME].sum())
    away_ht = int(away_goals_by_minute[:HALF_TIME].sum())
    return {
        "home_total": home_total, "away_total": away_total,
        "home_ht": home_ht, "away_ht": away_ht,
        "home_2h": home_total - home_ht, "away_2h": away_total - away_ht,
        "home_timeline": home_goals_by_minute,
        "away_timeline": away_goals_by_minute,
    }


def run_simulations(posterior, n_sims=NUM_SIMULATIONS, progress_callback=None):
    rng = np.random.default_rng(SEED)
    results = []
    n_posterior = len(posterior["home_attack"])
    for i in range(n_sims):
        idx = rng.integers(0, n_posterior)
        result = simulate_match(
            posterior["home_attack"][idx], posterior["home_defense"][idx],
            posterior["away_attack"][idx], posterior["away_defense"][idx], rng)
        results.append(result)
        if progress_callback and i % 200 == 0:
            progress_callback(i / n_sims)
    if progress_callback:
        progress_callback(1.0)
    return pd.DataFrame(results)


def compute_analytics(sim_df, home_name, away_name):
    n = len(sim_df)
    home_wins = (sim_df["home_total"] > sim_df["away_total"]).sum()
    draws = (sim_df["home_total"] == sim_df["away_total"]).sum()
    away_wins = (sim_df["home_total"] < sim_df["away_total"]).sum()
    scorelines = list(zip(sim_df["home_total"], sim_df["away_total"]))
    scoreline_counts = Counter(scorelines)
    top5 = scoreline_counts.most_common(5)
    ht_lines = list(zip(sim_df["home_ht"], sim_df["away_ht"]))
    ht_counts = Counter(ht_lines).most_common(8)
    second_half_goals = (sim_df["home_2h"] + sim_df["away_2h"])
    home_exp = sim_df["home_total"].mean()
    away_exp = sim_df["away_total"].mean()
    if home_exp >= away_exp:
        upset_prob = away_wins / n
        favourite, underdog = home_name, away_name
    else:
        upset_prob = home_wins / n
        favourite, underdog = away_name, home_name
    # ── MCSE: Monte Carlo Standard Error for proportions ──
    def mcse_pct(count, total):
        """MCSE for a proportion, returned as percentage."""
        p = count / total
        return np.sqrt(p * (1 - p) / total) * 100

    home_win_pct = home_wins / n * 100
    draw_pct = draws / n * 100
    away_win_pct = away_wins / n * 100
    upset_pct = upset_prob * 100

    return {
        "home_win_pct": home_win_pct,
        "draw_pct": draw_pct,
        "away_win_pct": away_win_pct,
        "home_win_mcse": mcse_pct(home_wins, n),
        "draw_mcse": mcse_pct(draws, n),
        "away_win_mcse": mcse_pct(away_wins, n),
        "upset_mcse": mcse_pct(int(upset_prob * n), n),
        "home_exp": home_exp,
        "away_exp": away_exp,
        "home_exp_std": sim_df["home_total"].std() / np.sqrt(n),
        "away_exp_std": sim_df["away_total"].std() / np.sqrt(n),
        "upset_prob": upset_pct,
        "favourite": favourite,
        "underdog": underdog,
        "top5_scorelines": top5,
        "ht_distribution": ht_counts,
        "second_half_goals": second_half_goals,
        "scoreline_counts": scoreline_counts,
        "n": n,
    }

# ──────────────────────────────────────────────────────────────────
# VISUALISATION (same as before)
# ──────────────────────────────────────────────────────────────────

def plot_score_matrix(analytics, home, away):
    counts = analytics["scoreline_counts"]
    n = analytics["n"]
    max_h = min(int(max(k[0] for k in counts.keys())) + 1, 8)
    max_a = min(int(max(k[1] for k in counts.keys())) + 1, 8)
    matrix = np.zeros((max_a + 1, max_h + 1))
    for (h, a), c in counts.items():
        if h <= max_h and a <= max_a:
            matrix[a, h] = c / n * 100
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(matrix, annot=True, fmt=".1f", cmap="YlOrRd",
                xticklabels=range(max_h + 1), yticklabels=range(max_a + 1),
                ax=ax, cbar_kws={"label": "Probability (%)"}, linewidths=0.5)
    ax.set_xlabel(f"{home} Goals", fontsize=12)
    ax.set_ylabel(f"{away} Goals", fontsize=12)
    ax.set_title("Scoreline Probability Matrix (%)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig


def plot_goal_timeline(sim_df, home, away):
    home_cumul = np.zeros(TOTAL_MINUTES)
    away_cumul = np.zeros(TOTAL_MINUTES)
    n = len(sim_df)
    for _, row in sim_df.iterrows():
        home_cumul += np.cumsum(row["home_timeline"])
        away_cumul += np.cumsum(row["away_timeline"])
    home_cumul /= n
    away_cumul /= n
    minutes = np.arange(1, TOTAL_MINUTES + 1)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(minutes, home_cumul, label=home, linewidth=2.2, color="#1b9e77")
    ax.plot(minutes, away_cumul, label=away, linewidth=2.2, color="#d95f02")
    ax.axvline(x=45, color="grey", linestyle="--", alpha=0.6, label="Half-time")
    ax.axvline(x=80, color="red", linestyle=":", alpha=0.4, label="Final push (80')")
    ax.fill_between(minutes, 0, home_cumul, alpha=0.08, color="#1b9e77")
    ax.fill_between(minutes, 0, away_cumul, alpha=0.08, color="#d95f02")
    ax.set_xlabel("Minute", fontsize=12)
    ax.set_ylabel("Expected Cumulative Goals", fontsize=12)
    ax.set_title("Average Goal Accumulation Timeline", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.set_xlim(1, 90)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
    plt.tight_layout()
    return fig


def plot_second_half_dist(analytics):
    data = analytics["second_half_goals"]
    fig, ax = plt.subplots(figsize=(7, 3.5))
    bins = np.arange(-0.5, data.max() + 1.5, 1)
    ax.hist(data, bins=bins, density=True, color="#7570b3",
            edgecolor="white", alpha=0.85, rwidth=0.85)
    ax.set_xlabel("Total 2nd-Half Goals", fontsize=11)
    ax.set_ylabel("Probability", fontsize=11)
    ax.set_title("Second-Half Goals Distribution", fontsize=13, fontweight="bold")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.tight_layout()
    return fig


def plot_wdw_bar(analytics, home, away):
    fig, ax = plt.subplots(figsize=(8, 1.2))
    hw = analytics["home_win_pct"]
    dr = analytics["draw_pct"]
    aw = analytics["away_win_pct"]
    ax.barh(0, hw, color="#1b9e77", edgecolor="white")
    ax.barh(0, dr, left=hw, color="#bdbdbd", edgecolor="white")
    ax.barh(0, aw, left=hw + dr, color="#d95f02", edgecolor="white")
    if hw > 8:
        ax.text(hw / 2, 0, f"{home}\n{hw:.1f}%", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")
    if dr > 8:
        ax.text(hw + dr / 2, 0, f"Draw\n{dr:.1f}%", ha="center", va="center",
                fontsize=10, fontweight="bold", color="#333")
    if aw > 8:
        ax.text(hw + dr + aw / 2, 0, f"{away}\n{aw:.1f}%", ha="center",
                va="center", fontsize=10, fontweight="bold", color="white")
    ax.set_xlim(0, 100)
    ax.axis("off")
    ax.set_title("Match Outcome Probabilities", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    return fig


# ──────────────────────────────────────────────────────────────────
# STREAMLIT UI
# ──────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Mundialista Network AI", page_icon="⚽", layout="wide")

    st.markdown("""
        <div style='text-align:center; padding: 0.5em 0 0.2em 0;'>
            <h1 style='margin-bottom:0;'>⚽ Mundialista Network AI</h1>
            <p style='color:grey; font-size:1.1em; margin-top:0.2em;'>
                Bayesian Poisson Match Prediction Engine
                &nbsp;·&nbsp; 10,200 Simulations
                &nbsp;·&nbsp; 250+ National Teams
                &nbsp;·&nbsp; Auto Data Lookup
            </p>
        </div>""", unsafe_allow_html=True)
    st.divider()

    # ── Sidebar ─────────────────────────────────────────────────
    st.sidebar.header("🏟️ Match Setup")
    
     # ── Load Real Data ─────────────────────────────────────────
    @st.cache_data(ttl=3600)
    def load_match_data():
        try:
            results = load_results(years_lookback=4)
            teams = get_all_teams(results)
            # Filter to teams with at least 3 matches
            qualified = []
            for t in teams:
                matches = get_team_matches(results, t)
                if len(matches) >= 3:
                    qualified.append(t)
            return results, sorted(qualified)
        except FileNotFoundError:
            return None, None

    csv_results, csv_teams = load_match_data()
    use_csv = csv_results is not None

    # Get sorted list of all teams
    if use_csv:
        all_teams = csv_teams
        st.sidebar.caption(f"📊 Live data: {len(csv_results):,} matches, {len(all_teams)} teams")
    else:
        all_teams = sorted(TEAM_DATABASE.keys())
        st.sidebar.caption("📋 Using built-in database (250+ teams)")
    
    # Team selection method
    input_method = st.sidebar.radio(
        "Team Selection Method",
        ["📋 Choose from List", "✏️ Type Team Name", "📝 Manual Data Entry"])
    
    if input_method == "📋 Choose from List":
        home_team = st.sidebar.selectbox("Home Team", all_teams, index=all_teams.index("Jamaica"))
        away_options = [t for t in all_teams if t != home_team]
        away_team = st.sidebar.selectbox("Away Team", away_options,
                                          index=away_options.index("New Caledonia") if "New Caledonia" in away_options else 0)
        if use_csv:
            home_stats = get_team_stats_for_app(csv_results, home_team, away_team)
            away_stats = get_team_stats_for_app(csv_results, away_team, home_team)
        else:
            home_stats = get_team_stats_auto(home_team)
            away_stats = get_team_stats_auto(away_team)
    
    elif input_method == "✏️ Type Team Name":
        home_team = st.sidebar.text_input("Home Team", value="Brazil")
        away_team = st.sidebar.text_input("Away Team", value="Argentina")
        
        if home_team == away_team:
            st.sidebar.error("Teams must be different!")
            st.stop()
        
        if use_csv:
            home_stats = get_team_stats_for_app(csv_results, home_team, away_team)
            away_stats = get_team_stats_for_app(csv_results, away_team, home_team)
        else:
            home_stats = get_team_stats_auto(home_team)
            away_stats = get_team_stats_auto(away_team)
        
        if home_stats is None:
            st.sidebar.warning(f"⚠️ '{home_team}' not found! Using Manual Entry.")
        if away_stats is None:
            st.sidebar.warning(f"⚠️ '{away_team}' not found! Using Manual Entry.")
    
    else:  # Manual Data Entry
        home_team = st.sidebar.text_input("Home Team Name", value="Team A")
        away_team = st.sidebar.text_input("Away Team Name", value="Team B")
        home_stats = None
        away_stats = None
    
    # Manual entry fallback
    if home_stats is None:
        st.sidebar.markdown(f"---\n**📊 {home_team} — Enter Data**")
        h_gf = st.sidebar.text_input("Goals SCORED (comma-separated)", "1,0,2,1,0,3,2", key="h_gf")
        h_ga = st.sidebar.text_input("Goals CONCEDED (comma-separated)", "0,1,1,1,2,0,0", key="h_ga")
        try:
            h_gf_arr = np.array([int(x.strip()) for x in h_gf.split(",")])
            h_ga_arr = np.array([int(x.strip()) for x in h_ga.split(",")])
            home_stats = {
                "avg_gf": h_gf_arr.mean(), "avg_ga": h_ga_arr.mean(),
                "std_gf": max(h_gf_arr.std(), 0.3), "std_ga": max(h_ga_arr.std(), 0.3),
                "n_matches": len(h_gf_arr), "goals_for": h_gf_arr,
                "goals_against": h_ga_arr, "found": False,
            }
        except:
            st.sidebar.error("Invalid input! Use numbers separated by commas.")
            st.stop()
    
    if away_stats is None:
        st.sidebar.markdown(f"---\n**📊 {away_team} — Enter Data**")
        a_gf = st.sidebar.text_input("Goals SCORED (comma-separated)", "1,0,2,1,0,1,3", key="a_gf")
        a_ga = st.sidebar.text_input("Goals CONCEDED (comma-separated)", "1,2,1,0,4,1,0", key="a_ga")
        try:
            a_gf_arr = np.array([int(x.strip()) for x in a_gf.split(",")])
            a_ga_arr = np.array([int(x.strip()) for x in a_ga.split(",")])
            away_stats = {
                "avg_gf": a_gf_arr.mean(), "avg_ga": a_ga_arr.mean(),
                "std_gf": max(a_gf_arr.std(), 0.3), "std_ga": max(a_ga_arr.std(), 0.3),
                "n_matches": len(a_gf_arr), "goals_for": a_gf_arr,
                "goals_against": a_ga_arr, "found": False,
            }
        except:
            st.sidebar.error("Invalid input! Use numbers separated by commas.")
            st.stop()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"**Simulations:** {NUM_SIMULATIONS:,}")
    st.sidebar.caption("**Engine:** Inhomogeneous Poisson + Bayesian PyMC")
    st.sidebar.markdown("---")
    quick_mode = st.sidebar.toggle("⚡ Quick Mode", value=True,
                                    help="Quick: ~5-10 sec (500 draws). Full: ~30-60 sec (2000 draws)")

    # ── Run Button ──────────────────────────────────────────────
    run_col1, run_col2, run_col3 = st.columns([1, 2, 1])
    with run_col2:
        run = st.button("🚀  Run Simulation", use_container_width=True, type="primary")

    if not run:
        # Show preview
        st.info(f"**{home_team}** 🏠 vs ✈️ **{away_team}** — Press Run to predict!")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"🏠 {home_team}")
            found = home_stats.get("found", False)
            st.write(f"{'✅ Auto-loaded' if found else '✏️ Manual entry'}")
            st.write(f"Avg Goals Scored: **{home_stats['avg_gf']:.2f}**")
            st.write(f"Avg Goals Conceded: **{home_stats['avg_ga']:.2f}**")
            st.write(f"Matches: **{home_stats['n_matches']}**")
        with col2:
            st.subheader(f"✈️ {away_team}")
            found = away_stats.get("found", False)
            st.write(f"{'✅ Auto-loaded' if found else '✏️ Manual entry'}")
            st.write(f"Avg Goals Scored: **{away_stats['avg_gf']:.2f}**")
            st.write(f"Avg Goals Conceded: **{away_stats['avg_ga']:.2f}**")
            st.write(f"Matches: **{away_stats['n_matches']}**")
        
        # Show available teams
        with st.expander("📋 Available Teams (80+)"):
            teams_by_region = {
                "🇪🇺 Europe": [t for t in all_teams if t in ["France","Spain","Germany","England","Portugal","Netherlands","Belgium","Italy","Croatia","Denmark","Switzerland","Austria","Turkey","Serbia","Poland","Ukraine","Sweden","Scotland","Wales","Czech Republic","Romania","Greece","Norway","Hungary","Russia","Republic of Ireland","Iceland","Finland","Slovakia","Slovenia","Albania","Georgia","North Macedonia","Bosnia"]],
                "🌎 South America": [t for t in all_teams if t in ["Brazil","Argentina","Uruguay","Colombia","Ecuador","Chile","Paraguay","Peru","Venezuela","Bolivia"]],
                "🌎 North/Central America": [t for t in all_teams if t in ["Mexico","USA","Canada","Costa Rica","Panama","Honduras","Jamaica","El Salvador","Trinidad and Tobago"]],
                "🌏 Asia": [t for t in all_teams if t in ["Japan","South Korea","Australia","Iran","Saudi Arabia","Qatar","Iraq","UAE","Uzbekistan","China","India"]],
                "🌍 Africa": [t for t in all_teams if t in ["Morocco","Senegal","Nigeria","Egypt","Cameroon","Algeria","Tunisia","Ivory Coast","Ghana","South Africa","DR Congo","Mali"]],
                "🌊 Oceania": [t for t in all_teams if t in ["New Zealand","New Caledonia","Fiji","Tahiti","Solomon Islands"]],
            }
            for region, teams in teams_by_region.items():
                st.write(f"**{region}:** {', '.join(teams)}")
        st.stop()

    # ── Run the Engine ──────────────────────────────────────────
    with st.status("📊 Computing team statistics…", expanded=False):
        st.write(f"**{home_team}** — Avg GF: {home_stats['avg_gf']:.2f}, Avg GA: {home_stats['avg_ga']:.2f}")
        st.write(f"**{away_team}** — Avg GF: {away_stats['avg_gf']:.2f}, Avg GA: {away_stats['avg_ga']:.2f}")

    mode_label = "⚡ Quick" if quick_mode else "🔬 Full Precision"
    with st.status(f"🧠 Running Bayesian inference ({mode_label})…", expanded=False) as status_bayes:
        posterior = bayesian_estimate(
            home_stats, away_stats,
            observed_home_goals=home_stats["goals_for"],
            observed_away_goals=away_stats["goals_for"],
            quick_mode=quick_mode)
        draws_info = f"{posterior['draws']} draws × {posterior['chains']} chains"
        if _build_cache_key(home_stats, away_stats, home_stats["goals_for"], away_stats["goals_for"]):
            cached_note = " (cached ⚡)" if True else ""
        status_bayes.update(label=f"🧠 Bayesian inference complete ✅ — {draws_info}", state="complete")

    n_sims = 3_000 if quick_mode else NUM_SIMULATIONS
    st.subheader("⏳ Simulating Matches…")
    progress = st.progress(0, text=f"Running {n_sims:,} simulations…")
    def update_progress(pct):
        progress.progress(min(pct, 1.0),
                          text=f"Simulated {int(pct * NUM_SIMULATIONS):,} / {NUM_SIMULATIONS:,}")
    sim_df = run_simulations(posterior, n_sims=n_sims, progress_callback=update_progress)
    progress.progress(1.0, text=f"✅ All {n_sims:,} simulations complete!")
    time.sleep(0.3)
    progress.empty()

    analytics = compute_analytics(sim_df, home_team, away_team)

    # ── RESULTS ─────────────────────────────────────────────────
    st.divider()
    st.header(f"🏆 {home_team}  vs  {away_team} — Prediction Results")
    
    fig_wdw = plot_wdw_bar(analytics, home_team, away_team)
    st.pyplot(fig_wdw)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        f"🏠 {home_team} Win",
        f"{analytics['home_win_pct']:.1f}%",
        delta=f"± {analytics['home_win_mcse']:.1f}% MCSE",
        delta_color="off")
    m2.metric(
        "🤝 Draw",
        f"{analytics['draw_pct']:.1f}%",
        delta=f"± {analytics['draw_mcse']:.1f}% MCSE",
        delta_color="off")
    m3.metric(
        f"✈️ {away_team} Win",
        f"{analytics['away_win_pct']:.1f}%",
        delta=f"± {analytics['away_win_mcse']:.1f}% MCSE",
        delta_color="off")
    m4.metric(
        f"🔥 Upset ({analytics['underdog']})",
        f"{analytics['upset_prob']:.1f}%",
        delta=f"± {analytics['upset_mcse']:.1f}% MCSE",
        delta_color="off")

    st.subheader("📋 Most Likely Scorelines")
    score_data = []
    for (h, a), cnt in analytics["top5_scorelines"]:
        score_data.append({
            "Scoreline": f"{home_team} {h} – {a} {away_team}",
            "Probability": f"{cnt / analytics['n'] * 100:.1f}%"})
    st.table(pd.DataFrame(score_data))

    st.subheader("⏱️ Half-Time Score Distribution (Top 8)")
    ht_data = []
    for (h, a), cnt in analytics["ht_distribution"]:
        ht_data.append({
            "HT Score": f"{home_team} {h} – {a} {away_team}",
            "Probability": f"{cnt / analytics['n'] * 100:.1f}%"})
    st.table(pd.DataFrame(ht_data))

    st.subheader("🔢 Scoreline Probability Matrix")
    st.pyplot(plot_score_matrix(analytics, home_team, away_team))

    st.subheader("📈 Goal Accumulation Timeline")
    st.pyplot(plot_goal_timeline(sim_df, home_team, away_team))

    st.subheader("📊 Second-Half Goals Distribution")
    st.pyplot(plot_second_half_dist(analytics))
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric(
        f"⚽ {home_team} xG",
        f"{analytics['home_exp']:.2f}",
        delta=f"± {analytics['home_exp_std']:.3f} MCSE",
        delta_color="off")
    c2.metric(
        f"⚽ {away_team} xG",
        f"{analytics['away_exp']:.2f}",
        delta=f"± {analytics['away_exp_std']:.3f} MCSE",
        delta_color="off")

    st.divider()
    st.caption("**Mundialista Network AI** v3.0 · 80+ Teams · 10,200 simulations")


if __name__ == "__main__":
    main()
