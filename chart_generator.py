import os
from pathlib import Path
import math

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from prediction_engine import get_score_matrix

# -----------------------------
# Theme
# -----------------------------
THEME = {
    "green": "#0F5C4D",
    "green_2": "#0B6B57",
    "green_3": "#16806A",
    "gold": "#C9A227",
    "gold_2": "#E1C15B",
    "ivory": "#F8F7F2",
    "white": "#FFFFFF",
    "charcoal": "#1E1E1E",
    "muted": "#6B7280",
    "light_gray": "#E8E6DE",
    "grid": "#D9D7CF"
}

OUTPUT_DIR = Path("predictions_output")
OUTPUT_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": THEME["ivory"],
    "axes.facecolor": THEME["white"],
    "axes.edgecolor": THEME["light_gray"],
    "axes.labelcolor": THEME["charcoal"],
    "xtick.color": THEME["charcoal"],
    "ytick.color": THEME["charcoal"],
    "text.color": THEME["charcoal"],
    "axes.titleweight": "bold",
    "axes.titlesize": 14,
    "font.size": 11,
    "font.family": "DejaVu Sans",
    "grid.color": THEME["grid"],
    "grid.alpha": 0.35,
    "axes.grid": False,
    "savefig.facecolor": THEME["ivory"],
    "savefig.edgecolor": THEME["ivory"]
})

# -----------------------------
# Helpers
# -----------------------------
def slugify(text):
    return (
        str(text).strip().lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

def base_filename(team_a, team_b):
    return f"{slugify(team_a)}_vs_{slugify(team_b)}"

def save_fig(fig, filename):
    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return str(path)

def soft_card(ax):
    rect = patches.FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        transform=ax.transAxes,
        linewidth=1,
        edgecolor=THEME["light_gray"],
        facecolor=THEME["white"],
        zorder=-10
    )
    ax.add_patch(rect)

def make_title(ax, title, subtitle=None):
    ax.set_title(title, loc="left", color=THEME["green"], pad=14, fontsize=15, fontweight="bold")
    if subtitle:
        ax.text(
            0.0, 1.02, subtitle,
            transform=ax.transAxes,
            fontsize=9.5,
            color=THEME["muted"],
            va="bottom"
        )

def build_insight(result, team_a, team_b):
    a = result.get("team_a_win", 0)
    d = result.get("draw", 0)
    b = result.get("team_b_win", 0)
    la = result.get("team_a_lambda", 0)
    lb = result.get("team_b_lambda", 0)
    match_type = result.get("match_type", "Competitive")

    if abs(a - b) <= 6:
        edge = f"{team_a} and {team_b} project as closely matched."
    elif a > b:
        edge = f"{team_a} hold the model edge."
    else:
        edge = f"{team_b} hold the model edge."

    if d >= 27:
        draw_note = "Draw probability is elevated, suggesting limited separation."
    elif d <= 20:
        draw_note = "A decisive result is more likely than usual."
    else:
        draw_note = "The draw remains a meaningful live outcome."

    total_lambda = la + lb
    if total_lambda >= 2.9:
        goals_note = "Expected goals suggest a more open scoring environment."
    elif total_lambda <= 2.3:
        goals_note = "Expected goals point to a tighter, lower-scoring match."
    else:
        goals_note = "Expected goals sit in a moderate range."

    return f"{match_type}. {edge} {draw_note} {goals_note}"

# -----------------------------
# Chart 1: Summary card
# -----------------------------
def generate_summary_chart(result, team_a, team_b):
    fig = plt.figure(figsize=(12, 5), facecolor=THEME["ivory"])
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.84])
    ax.axis("off")

    card = patches.FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.2,
        edgecolor=THEME["light_gray"],
        facecolor=THEME["white"]
    )
    ax.add_patch(card)

    ax.text(0.04, 0.88, "Mundialista AI", fontsize=20, fontweight="bold", color=THEME["green"])
    ax.text(0.04, 0.82, "International Match Intelligence", fontsize=10.5, color=THEME["muted"])

    ax.text(0.04, 0.64, team_a, fontsize=20, fontweight="bold", color=THEME["green"])
    ax.text(0.04, 0.57, f"FIFA Rank: {result.get('team_a_rank', 'N/A')}", fontsize=10.5, color=THEME["muted"])

    ax.text(0.50, 0.64, "VS", fontsize=14, fontweight="bold", color=THEME["gold"], ha="center",
            bbox=dict(boxstyle="round,pad=0.35", fc="#FFF8E1", ec="#E7D7A3"))

    ax.text(0.96, 0.64, team_b, fontsize=20, fontweight="bold", color=THEME["green"], ha="right")
    ax.text(0.96, 0.57, f"FIFA Rank: {result.get('team_b_rank', 'N/A')}", fontsize=10.5, color=THEME["muted"], ha="right")

    stats = [
        (f"{team_a} Win", f"{result.get('team_a_win', 0):.1f}%", THEME["green"]),
        ("Draw", f"{result.get('draw', 0):.1f}%", "#8A6B00"),
        (f"{team_b} Win", f"{result.get('team_b_win', 0):.1f}%", THEME["green"]),
        (f"{team_a} ?", f"{result.get('team_a_lambda', 0):.2f}", THEME["green"]),
        (f"{team_b} ?", f"{result.get('team_b_lambda', 0):.2f}", THEME["green"]),
        ("Match Type", f"{result.get('match_type', 'Competitive')}", THEME["gold"]),
    ]

    x_positions = [0.05, 0.215, 0.38, 0.545, 0.71, 0.83]
    widths =      [0.14, 0.14, 0.14, 0.14, 0.14, 0.12]

    for (label, value, color), x, w in zip(stats, x_positions, widths):
        box = patches.FancyBboxPatch(
            (x, 0.18), w, 0.20,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            linewidth=1,
            edgecolor=THEME["light_gray"],
            facecolor=THEME["ivory"]
        )
        ax.add_patch(box)
        ax.text(x + 0.015, 0.31, label, fontsize=9, color=THEME["muted"])
        ax.text(x + 0.015, 0.22, value, fontsize=16, fontweight="bold", color=color)

    insight = build_insight(result, team_a, team_b)
    ax.text(
        0.04, 0.08, insight,
        fontsize=10, color=THEME["charcoal"],
        bbox=dict(boxstyle="round,pad=0.5", fc="#FFFDF6", ec="#EADCA8")
    )

    return save_fig(fig, f"{base_filename(team_a, team_b)}_summary.png")

# -----------------------------
# Chart 2: Probability bar chart
# -----------------------------
def generate_probability_chart(result, team_a, team_b):
    labels = [f"{team_a} Win", "Draw", f"{team_b} Win"]
    values = [result.get("team_a_win", 0), result.get("draw", 0), result.get("team_b_win", 0)]
    colors = [THEME["green"], THEME["gold"], "#7B8391"]

    fig, ax = plt.subplots(figsize=(9, 5))
    soft_card(ax)

    bars = ax.bar(labels, values, color=colors, width=0.58)

    make_title(ax, "Win / Draw / Loss Probability", "Model-estimated outcome distribution")
    ax.set_ylabel("Probability (%)")
    ax.set_ylim(0, max(values) + 12)
    ax.grid(axis="y", linestyle="-", alpha=0.18)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.8,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color=THEME["charcoal"]
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return save_fig(fig, f"{base_filename(team_a, team_b)}_probability.png")

# -----------------------------
# Chart 3: Score matrix heatmap
# -----------------------------
def generate_score_matrix_chart(result, team_a, team_b, max_goals=5):
    matrix = get_score_matrix(result.get("team_a_lambda", 0), result.get("team_b_lambda", 0), max_goals=max_goals)
    fig, ax = plt.subplots(figsize=(8.5, 6.2))
    soft_card(ax)

    im = ax.imshow(matrix, cmap="Greens", origin="upper")

    make_title(ax, "Exact Score Probability Matrix", "Darker cells indicate more likely scorelines")
    ax.set_xlabel(f"{team_b} goals")
    ax.set_ylabel(f"{team_a} goals")
    ax.set_xticks(range(max_goals + 1))
    ax.set_yticks(range(max_goals + 1))

    top_indices = np.dstack(np.unravel_index(np.argsort(matrix.ravel())[::-1][:3], matrix.shape))[0]
    for i, j in top_indices:
        rect = patches.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=THEME["gold"], linewidth=2)
        ax.add_patch(rect)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            ax.text(j, i, f"{val*100:.1f}", ha="center", va="center",
                    color="white" if val > matrix.max() * 0.55 else THEME["charcoal"], fontsize=8.5)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Probability")
    cbar.outline.set_edgecolor(THEME["light_gray"])

    return save_fig(fig, f"{base_filename(team_a, team_b)}_matrix.png")

# -----------------------------
# Chart 4: Top scorelines
# -----------------------------
def generate_top_scores_chart(result, team_a, team_b, top_n=8):
    top_scores = result.get("top_scores", [])[:top_n]

    labels = []
    values = []

    for item in top_scores:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            labels.append(str(item[0]))
            values.append(float(item[1]))
        else:
            labels.append(str(item))
            values.append(0)

    if not labels:
        labels = ["1-1", "1-0", "0-1"]
        values = [1, 0.8, 0.7]

    fig, ax = plt.subplots(figsize=(10, 5.4))
    soft_card(ax)

    y = np.arange(len(labels))
    colors = [THEME["green"] if i == 0 else "#9BBCAF" for i in range(len(labels))]
    bars = ax.barh(y, values, color=colors, height=0.62)

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()

    make_title(ax, "Most Likely Exact Scorelines", "Top score outcomes returned by simulation/model output")
    ax.set_xlabel("Relative likelihood / count")
    ax.grid(axis="x", linestyle="-", alpha=0.16)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + max(values)*0.012, bar.get_y() + bar.get_height()/2,
                f"{val:.0f}", va="center", fontsize=10, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return save_fig(fig, f"{base_filename(team_a, team_b)}_top_scores.png")

# -----------------------------
# Chart 5: Goal distribution histograms
# -----------------------------
def poisson_pmf(k, lam):
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def generate_goal_distribution_chart(result, team_a, team_b, max_goals=6):
    la = result.get("team_a_lambda", 0)
    lb = result.get("team_b_lambda", 0)

    goals = np.arange(0, max_goals + 1)
    pa = np.array([poisson_pmf(k, la) for k in goals]) * 100
    pb = np.array([poisson_pmf(k, lb) for k in goals]) * 100

    fig, ax = plt.subplots(figsize=(10, 5.2))
    soft_card(ax)

    width = 0.38
    ax.bar(goals - width/2, pa, width=width, color=THEME["green"], label=team_a)
    ax.bar(goals + width/2, pb, width=width, color=THEME["gold"], label=team_b)

    make_title(ax, "Goal Distribution", "Independent Poisson goal likelihood by team")
    ax.set_xlabel("Goals scored")
    ax.set_ylabel("Probability (%)")
    ax.set_xticks(goals)
    ax.legend(frameon=False)
    ax.grid(axis="y", linestyle="-", alpha=0.16)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return save_fig(fig, f"{base_filename(team_a, team_b)}_goals.png")

# -----------------------------
# HTML report
# -----------------------------
def generate_html_report(result, team_a, team_b, chart_paths):
    html_path = OUTPUT_DIR / f"{base_filename(team_a, team_b)}.html"

    insight = build_insight(result, team_a, team_b)

    score_items = ""
    for item in result.get("top_scores", [])[:6]:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            score_items += f'<span class="score-pill">{item[0]}  -  {item[1]}</span>'
        else:
            score_items += f'<span class="score-pill">{item}</span>'

    html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mundialista AI Report — {team_a} vs {team_b}</title>
<style>
:root {{
    --green: #0F5C4D;
    --green2: #0B6B57;
    --gold: #C9A227;
    --ivory: #F8F7F2;
    --white: #FFFFFF;
    --text: #1E1E1E;
    --muted: #6B7280;
    --border: rgba(15, 92, 77, 0.12);
    --shadow: 0 8px 24px rgba(0,0,0,0.05);
    --radius: 20px;
}}
* {{
    box-sizing: border-box;
}}
body {{
    margin: 0;
    background: var(--ivory);
    color: var(--text);
    font-family: "Segoe UI", Arial, sans-serif;
}}
.container {{
    max-width: 1180px;
    margin: 0 auto;
    padding: 32px 20px 48px;
}}
.hero {{
    background: linear-gradient(135deg, var(--green), var(--green2));
    color: white;
    border-radius: 28px;
    padding: 32px;
    box-shadow: var(--shadow);
    margin-bottom: 24px;
}}
.hero h1 {{
    margin: 0 0 6px 0;
    font-size: 2.25rem;
}}
.hero p {{
    margin: 6px 0;
    color: rgba(255,255,255,0.88);
}}
.hero .tag {{
    display: inline-block;
    margin-top: 12px;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(201,162,39,0.18);
    border: 1px solid rgba(201,162,39,0.3);
    color: #F7E7B0;
    font-weight: 700;
    font-size: 0.85rem;
}}
.card {{
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px;
    box-shadow: var(--shadow);
    margin-bottom: 18px;
}}
.section-title {{
    color: var(--green);
    margin: 0 0 14px 0;
    font-size: 1.1rem;
}}
.vs {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 14px;
}}
.team {{
    font-size: 1.45rem;
    font-weight: 800;
    color: var(--green);
}}
.rank {{
    color: var(--muted);
    margin-top: 4px;
}}
.vs-badge {{
    padding: 10px 14px;
    border-radius: 999px;
    background: rgba(201,162,39,0.12);
    border: 1px solid rgba(201,162,39,0.25);
    color: #8A6B00;
    font-weight: 800;
}}
.metrics {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin-top: 18px;
}}
.metric {{
    background: #FCFCFA;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px;
}}
.metric .label {{
    color: var(--muted);
    font-size: 0.82rem;
    margin-bottom: 6px;
}}
.metric .value {{
    color: var(--green);
    font-size: 1.45rem;
    font-weight: 800;
}}
.badges {{
    margin-top: 14px;
}}
.badge {{
    display: inline-block;
    padding: 7px 10px;
    border-radius: 999px;
    margin-right: 8px;
    font-size: 0.8rem;
    font-weight: 700;
}}
.badge-green {{
    background: rgba(15,92,77,0.10);
    color: var(--green);
    border: 1px solid rgba(15,92,77,0.18);
}}
.badge-gold {{
    background: rgba(201,162,39,0.14);
    color: #8A6B00;
    border: 1px solid rgba(201,162,39,0.25);
}}
.insight {{
    border-left: 4px solid var(--gold);
    background: #FFFDF6;
    padding: 14px 16px;
    border-radius: 12px;
    line-height: 1.55;
}}
.grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}}
.chart-card img {{
    width: 100%;
    border-radius: 14px;
    border: 1px solid var(--border);
}}
.score-pill {{
    display: inline-block;
    padding: 9px 12px;
    border-radius: 12px;
    background: #FAFAF7;
    border: 1px solid var(--border);
    margin: 6px 8px 0 0;
    color: var(--green);
    font-weight: 700;
}}
.footer {{
    text-align: center;
    color: var(--muted);
    margin-top: 24px;
    font-size: 0.9rem;
}}
@media (max-width: 900px) {{
    .metrics {{
        grid-template-columns: repeat(2, 1fr);
    }}
    .grid {{
        grid-template-columns: 1fr;
    }}
    .vs {{
        flex-direction: column;
        align-items: flex-start;
    }}
}}
</style>
</head>
<body>
<div class="container">
    <div class="hero">
        <h1>Mundialista AI</h1>
        <p>International Match Intelligence</p>
        <p>{team_a} vs {team_b}</p>
        <span class="tag">Refined match forecast report</span>
    </div>

    <div class="card">
        <div class="vs">
            <div>
                <div class="team">{team_a}</div>
                <div class="rank">FIFA Rank: {result.get("team_a_rank", "N/A")}</div>
            </div>
            <div class="vs-badge">VS</div>
            <div style="text-align:right;">
                <div class="team">{team_b}</div>
                <div class="rank">FIFA Rank: {result.get("team_b_rank", "N/A")}</div>
            </div>
        </div>

        <div class="badges">
            <span class="badge badge-gold">{result.get("match_type", "Competitive")}</span>
            <span class="badge badge-green">Monte Carlo Forecast</span>
        </div>

        <div class="metrics">
            <div class="metric"><div class="label">{team_a} Win</div><div class="value">{result.get("team_a_win", 0):.1f}%</div></div>
            <div class="metric"><div class="label">Draw</div><div class="value" style="color:#8A6B00;">{result.get("draw", 0):.1f}%</div></div>
            <div class="metric"><div class="label">{team_b} Win</div><div class="value">{result.get("team_b_win", 0):.1f}%</div></div>
            <div class="metric"><div class="label">{team_a} ?</div><div class="value">{result.get("team_a_lambda", 0):.2f}</div></div>
            <div class="metric"><div class="label">{team_b} ?</div><div class="value">{result.get("team_b_lambda", 0):.2f}</div></div>
            <div class="metric"><div class="label">Model</div><div class="value" style="font-size:1.1rem;">Poisson + Form</div></div>
        </div>
    </div>

    <div class="card">
        <h3 class="section-title">Model Insight</h3>
        <div class="insight">{insight}</div>
    </div>

    <div class="card">
        <h3 class="section-title">Most Likely Scorelines</h3>
        <div>{score_items}</div>
    </div>

    <div class="grid">
        <div class="card chart-card">
            <h3 class="section-title">Probability Profile</h3>
            <img src="{os.path.basename(chart_paths['probability'])}" alt="Probability chart">
        </div>
        <div class="card chart-card">
            <h3 class="section-title">Score Matrix</h3>
            <img src="{os.path.basename(chart_paths['matrix'])}" alt="Score matrix chart">
        </div>
        <div class="card chart-card">
            <h3 class="section-title">Top Scorelines</h3>
            <img src="{os.path.basename(chart_paths['top_scores'])}" alt="Top scores chart">
        </div>
        <div class="card chart-card">
            <h3 class="section-title">Goal Distribution</h3>
            <img src="{os.path.basename(chart_paths['goals'])}" alt="Goal distribution chart">
        </div>
    </div>

    <div class="footer">
        Mundialista AI • International football prediction system
    </div>
</div>
</body>
</html>
'''
    html_path.write_text(html, encoding="utf-8")
    return str(html_path)

# -----------------------------
# Main public API
# -----------------------------
def generate_all_charts(result, team_a, team_b):
    chart_paths = {}
    chart_paths["summary"] = generate_summary_chart(result, team_a, team_b)
    chart_paths["probability"] = generate_probability_chart(result, team_a, team_b)
    chart_paths["matrix"] = generate_score_matrix_chart(result, team_a, team_b)
    chart_paths["top_scores"] = generate_top_scores_chart(result, team_a, team_b)
    chart_paths["goals"] = generate_goal_distribution_chart(result, team_a, team_b)
    chart_paths["html"] = generate_html_report(result, team_a, team_b, chart_paths)
    return chart_paths


