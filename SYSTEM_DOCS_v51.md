# Mundialista AI - v5.1 Premium Update
# Complete System Documentation
# Last Updated: March 2026

---

# 1. Update Overview

## What is Mundialista AI?

A Python-based international football match prediction system that:
- Predicts match outcomes using Poisson Monte Carlo simulation (10,200 iterations)
- Uses real FIFA rankings (201 teams) + historical match data (4,200+ matches)
- Tracks star players for 21 nations with attack boost multipliers
- Generates visualizations (5 chart types + HTML reports)
- Has both CLI (terminal) and Web (Streamlit) interfaces
- Both interfaces use the SAME prediction engine for consistent results
- Both interfaces ALWAYS generate charts on every prediction

## What changed in v5 and v5.1?

A complete visual identity overhaul unifying look and feel across all surfaces.

| Surface          | Before                                    | After                                              |
|------------------|-------------------------------------------|----------------------------------------------------|
| Streamlit Web    | Blue/red/gray, sidebar, no charts         | Green/gold/ivory, cards, tabbed charts, download   |
| CLI Charts PNGs  | Dark theme or default matplotlib          | Ivory backgrounds, green/gold palette, refined     |
| HTML Reports     | Basic or dark themed                      | Premium responsive cards, branded hero, editorial  |
| CLI Text Output  | Basic print statements                    | Aligned columns, dividers, always generates charts |

## Design System

| Element            | Value     |
|--------------------|-----------|
| Deep Green         | #0F5C4D   |
| Secondary Green    | #0B6B57   |
| Rich Gold          | #C9A227   |
| Soft Gold          | #E9D48A   |
| Ivory Background   | #F8F7F2   |
| White Cards        | #FFFFFF   |
| Charcoal Text      | #1E1E1E   |
| Muted Gray         | #6B7280   |

## Current Features

- Premium hero banner in Streamlit and HTML reports
- Card-based layout throughout
- Badge system (match type, venue)
- Probability progress bars (green/gold/gray)
- Model insight narrative generator
- Score pills for top scorelines
- Consistent branding: Mundialista AI - International Match Intelligence
- Cached predictions in Streamlit via st.cache_data
- Session state persistence in Streamlit (results survive reruns)
- Loading spinner during prediction generation
- 5 tabbed chart views in Streamlit
- HTML report download button in Streamlit
- Charts ALWAYS generated in CLI (no flag needed)
- Cleaner CLI output with aligned columns
- Interactive CLI mode with prompts
- HTML reports with responsive grid and chart embedding
- Gold-outlined top 3 scores in heatmap
- Poisson goal distribution chart (green vs gold bars)

---

# 2. What Changed (File by File)

## app.py (root) - Streamlit Web Interface
Status: Fully rewritten in v5, updated in v5.1

Imports:
    import matplotlib (with Agg backend)
    import streamlit as st
    import pandas as pd
    import os
    from prediction_engine import predict, load_rankings
    from chart_generator import generate_all_charts

Key features:
- matplotlib backend set to Agg (prevents display conflicts)
- Full custom CSS with green/gold/ivory variables
- Hero banner component
- Card-based match setup section
- Metric boxes for win/draw/loss
- Probability progress bars
- Expected goals display
- Score pills for top scorelines
- Model insight narrative
- st.cache_data for team list loading
- st.session_state for persisting results and chart paths
- Loading spinner during prediction
- 5 tabbed chart views showing generated PNGs
- HTML report download button
- Raw prediction output expander
- Badge system for match type and venue
- String concatenation (not f-strings) for PowerShell safety

## chart_generator.py - Chart and Report Generator
Status: Fully rewritten in v5

Key features:
- Unified THEME dictionary with all brand colors
- Global matplotlib rcParams for ivory/white/green
- soft_card() helper for card backgrounds
- make_title() helper for green titles
- build_insight() narrative generator
- slugify() and base_filename() for file naming

Charts generated:
- Summary Card: branded scorecard with VS badge, metrics, insight
- Probability Bar: green/gold/gray bars with percentage labels
- Score Matrix: Greens colormap, gold outlines on top 3, percentages
- Top Scorelines: horizontal bars, green primary, muted secondary
- Goal Distribution: side-by-side green/gold Poisson bars

HTML Report:
- Responsive CSS with variables
- Hero banner matching Streamlit
- VS card with teams, ranks, badges
- 6-column metrics grid
- Insight section with gold left border
- Score pills section
- 2-column chart grid
- Mobile responsive
- Footer branding

Function: generate_all_charts(result, team_a, team_b)
Returns dict with keys: summary, probability, matrix, top_scores, goals, html

## predict.py - CLI Interface
Status: Fully rewritten in v5.1

Key features:
- Charts ALWAYS generate (no --charts flag exists)
- Only flag: --open (-o) to open HTML in browser
- Clean print_result() with aligned columns
- print_divider() for visual separation
- interactive_mode() with prompts
- Prints all generated file paths

Usage:
    python predict.py Argentina Brazil
    python predict.py Argentina Brazil --open
    python predict.py                          (interactive)

## .streamlit/config.toml - Streamlit Theme
Status: Created in v5
Sets: gold primary, ivory background, white cards, charcoal text

## mundialista-ai/app.py - Deploy Wrapper
Status: Unchanged
Routes Streamlit Cloud to root app.py via runpy.run_path()

## prediction_engine.py - Core Engine
Status: Unchanged in v5 and v5.1
All prediction logic, CONFIG, STAR_PLAYERS, simulation unchanged.

## Files NOT Modified
- prediction_engine.py
- data/results.csv
- data/rankings.csv
- data/goalscorers.csv
- data/shootouts.csv
- mundialista-ai/app.py (wrapper)

---

# 3. Save Everything to Git

    cd C:\Users\bayen\mundialista-ai
    .\venv\Scripts\Activate.ps1
    git status
    git add app.py chart_generator.py predict.py .streamlit/config.toml .gitignore
    git status
    git commit -m "v5.1: Charts always generated in CLI and Streamlit tabs"
    git push
    git log --oneline -5

---

# 4. Verify Everything Locally

Syntax checks (all should produce no output):
    python -m py_compile app.py
    python -m py_compile chart_generator.py
    python -m py_compile predict.py
    python -m py_compile prediction_engine.py
    python -m py_compile .\mundialista-ai\app.py

Engine test:
    python -c "from prediction_engine import predict; r=predict('Argentina','Brazil'); print(r['team_a_win'], r['draw'], r['team_b_win'])"

Chart generation test:
    python -c "from prediction_engine import predict; from chart_generator import generate_all_charts; r=predict('Argentina','Brazil'); charts=generate_all_charts(r,'Argentina','Brazil'); print(charts)"

CLI test (always generates charts):
    python predict.py Argentina Brazil

CLI with auto-open:
    python predict.py Argentina Brazil --open

CLI interactive:
    python predict.py

Streamlit test:
    streamlit run app.py

Verify in browser at http://localhost:8501:
    - Green/gold/ivory theme loads
    - Hero banner shows Mundialista AI
    - Select two teams and click Generate Prediction
    - Spinner appears
    - Metrics, probabilities, insight appear
    - 5 tabbed charts appear
    - Download Full HTML Report button works
    - Raw output expander works

Open generated files:
    ii predictions_output
    ii .\predictions_output\argentina_vs_brazil.html
    ii .\predictions_output\argentina_vs_brazil_summary.png

Data check:
    python -c "import pandas as pd; print('Matches:', len(pd.read_csv('data/results.csv'))); print('Teams:', len(pd.read_csv('data/rankings.csv')))"

---

# 5. Verify Deployment

After git push, Streamlit Cloud auto-redeploys.

Check:
1. Go to Streamlit Cloud dashboard
2. Wait for rebuild
3. Verify hero banner, theme, prediction, tabbed charts, download

If deployment fails check logs for:
- ImportError: missing export from prediction_engine.py
- FileNotFoundError: missing data files
- SyntaxError: file corruption

Debug imports:
    Get-Content prediction_engine.py | Select-String "^def " -Context 0,0

---

# 6. Updated System Context

Version: v5.1

Architecture:
    mundialista-ai/
    |-- prediction_engine.py         (core engine, unchanged)
    |-- chart_generator.py           (v5: green/gold/ivory charts)
    |-- app.py                       (v5.1: premium UI + tabbed charts)
    |-- predict.py                   (v5.1: always generates charts)
    |-- mundialista-ai/app.py        (deploy wrapper, unchanged)
    |-- .streamlit/config.toml       (v5: theme)
    |-- .gitignore                   (v5: excludes backups/output)
    |-- data/results.csv
    |-- data/rankings.csv
    |-- data/goalscorers.csv
    |-- data/shootouts.csv
    |-- predictions_output/          (generated, not committed)

Key API:
    from prediction_engine import predict, load_rankings
    result = predict("Argentina", "Brazil")

    from chart_generator import generate_all_charts
    charts = generate_all_charts(result, "Argentina", "Brazil")
    # Returns: summary, probability, matrix, top_scores, goals, html

Quick Commands:
    cd C:\Users\bayen\mundialista-ai
    .\venv\Scripts\Activate.ps1

    python predict.py Argentina Brazil
    python predict.py Argentina Brazil --open
    python predict.py
    streamlit run app.py

---

# 7. Known Issues and Notes

## PowerShell encoding
All .py files must be saved as UTF-8:
    Set-Content filename.py -Encoding utf8

## Special characters to avoid in PowerShell heredocs
- Dollar sign (PowerShell variable interpolation)
- Middle dot
- Em dash, en dash
- Smart quotes
Use string concatenation in Python instead of f-strings.

## Streamlit caching
Cached: team list, prediction results
If data files update, clear cache or restart.

## Streamlit chart generation
Charts generated inside Streamlit on every prediction.
Adds a few seconds. Spinner shows during generation.
Session state keeps results persistent across reruns.

## 1-1 scoreline dominance
Most matchups show 1-1 as most probable score.
Known model characteristic. To reduce, change in prediction_engine.py:
    DRAW_PULL: 0.10 (was 0.20)
    CONVERGENCE_PULL: 0.25 (was 0.40)
    MAX_RATIO: 1.20 (was 1.15)
NOT changed in v5/v5.1. Engine untouched.

## Streamlit speed
Main delay sources:
- Chart generation (5 PNGs + HTML) each prediction
- CSV loading (mitigated by caching)
- Prediction computation (mitigated by caching)

Future improvements:
- Replace Monte Carlo with exact Poisson matrix
- Vectorize simulation with NumPy
- Add Numba for numeric hotspots
- Reduce chart DPI
- Cache chart outputs by matchup

---

# 8. Emergency Rollback

Revert to previous commit:
    git log --oneline -10
    git checkout COMMITHASH -- app.py chart_generator.py predict.py
    git add -A
    git commit -m "Rollback to pre-v5.1"
    git push

Or revert last commit:
    git revert HEAD
    git push

Restore from local backups:
    Get-ChildItem *backup* | Select-Object Name, LastWriteTime
    Copy-Item backup-file target-file

---

# Final Checklist

    python -m py_compile app.py
    python -m py_compile chart_generator.py
    python -m py_compile predict.py
    python -m py_compile prediction_engine.py
    python -c "from prediction_engine import predict; r=predict('France','England'); print(r['team_a_win'])"
    python -c "from prediction_engine import predict; from chart_generator import generate_all_charts; r=predict('France','England'); print(generate_all_charts(r,'France','England'))"
    python predict.py Spain Germany
    python predict.py Brazil Bolivia --open
    streamlit run app.py
    git status
    git log --oneline -3
    git push
