# chart_generator.py - Generate charts for CLI and Streamlit
"""
Generates all visualizations for Mundialista-AI.
Works with both CLI (saves files) and Streamlit (returns figures).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import os
from datetime import datetime

# Create output directory
OUTPUT_DIR = "predictions_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_all_charts(result: dict, save: bool = True, show: bool = False) -> dict:
    """
    Generate all charts for a prediction.
    
    Args:
        result: Prediction result from predict()
        save: Save charts to files
        show: Display charts (for CLI)
    
    Returns:
        Dictionary with file paths
    """
    team_a = result['team_a']
    team_b = result['team_b']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{OUTPUT_DIR}/{team_a}_vs_{team_b}_{timestamp}"
    
    charts = {}
    
    # 1. Win Probability Bar Chart
    charts['probability'] = generate_probability_chart(result, prefix, save, show)
    
    # 2. Score Matrix Heatmap
    charts['matrix'] = generate_score_matrix_chart(result, prefix, save, show)
    
    # 3. Goal Distribution
    charts['goals'] = generate_goal_distribution(result, prefix, save, show)
    
    # 4. Top Scores Bar Chart
    charts['top_scores'] = generate_top_scores_chart(result, prefix, save, show)
    
    # 5. Match Summary Card
    charts['summary'] = generate_summary_card(result, prefix, save, show)
    
    return charts


def generate_probability_chart(result: dict, prefix: str, save: bool, show: bool):
    """Horizontal bar chart showing win/draw/loss probabilities"""
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    team_a = result['team_a']
    team_b = result['team_b']
    
    categories = [f"{team_a} Win", "Draw", f"{team_b} Win"]
    values = [result['team_a_win'], result['draw'], result['team_b_win']]
    colors = ['#3498db', '#95a5a6', '#e74c3c']
    
    bars = ax.barh(categories, values, color=colors, height=0.6, edgecolor='white', linewidth=2)
    
    for bar, val in zip(bars, values):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{val}%', va='center', fontsize=14, fontweight='bold')
    
    ax.set_xlim(0, 100)
    ax.set_xlabel('Probability (%)', fontsize=12)
    ax.set_title(f'Match Prediction: {team_a} vs {team_b}', fontsize=16, fontweight='bold')
    
    ax.text(0.98, 0.02, f"Match Type: {result['match_type']}", 
            transform=ax.transAxes, ha='right', fontsize=10, 
            style='italic', color='gray')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    filepath = f"{prefix}_probability.png" if save else None
    if save:
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {filepath}")
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return filepath


def generate_score_matrix_chart(result: dict, prefix: str, save: bool, show: bool):
    """Heatmap showing probability of each scoreline"""
    
    from prediction_engine import get_score_matrix
    
    matrix = get_score_matrix(result['team_a_lambda'], result['team_b_lambda'], max_goals=5)
    matrix_pct = matrix * 100
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    cmap = LinearSegmentedColormap.from_list('custom', ['#ffffff', '#3498db', '#1a5276'])
    
    im = ax.imshow(matrix_pct, cmap=cmap, aspect='equal')
    
    ax.set_xticks(range(6))
    ax.set_yticks(range(6))
    ax.set_xticklabels(range(6), fontsize=12)
    ax.set_yticklabels(range(6), fontsize=12)
    ax.set_xlabel(f"{result['team_b']} Goals", fontsize=14)
    ax.set_ylabel(f"{result['team_a']} Goals", fontsize=14)
    
    for i in range(6):
        for j in range(6):
            val = matrix_pct[i, j]
            color = 'white' if val > 5 else 'black'
            ax.text(j, i, f'{val:.1f}%', ha='center', va='center', 
                   fontsize=9, color=color, fontweight='bold' if val > 8 else 'normal')
    
    ax.set_title(f'Score Probability Matrix\n{result["team_a"]} vs {result["team_b"]}', 
                fontsize=14, fontweight='bold')
    
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Probability (%)', fontsize=11)
    
    plt.tight_layout()
    
    filepath = f"{prefix}_matrix.png" if save else None
    if save:
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {filepath}")
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return filepath


def generate_goal_distribution(result: dict, prefix: str, save: bool, show: bool):
    """Histogram showing distribution of goals for each team"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    goals_a = result['goals_a']
    goals_b = result['goals_b']
    
    max_goal = max(max(goals_a), max(goals_b), 6)
    bins = range(0, max_goal + 2)
    
    ax1.hist(goals_a, bins=bins, color='#3498db', edgecolor='white', 
             linewidth=1.5, alpha=0.8, align='left')
    ax1.axvline(result['team_a_lambda'], color='red', linestyle='--', 
                linewidth=2, label=f'Expected: {result["team_a_lambda"]:.2f}')
    ax1.set_xlabel('Goals', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title(f'{result["team_a"]} Goal Distribution', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.set_xlim(-0.5, 7.5)
    
    ax2.hist(goals_b, bins=bins, color='#e74c3c', edgecolor='white', 
             linewidth=1.5, alpha=0.8, align='left')
    ax2.axvline(result['team_b_lambda'], color='blue', linestyle='--', 
                linewidth=2, label=f'Expected: {result["team_b_lambda"]:.2f}')
    ax2.set_xlabel('Goals', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.set_title(f'{result["team_b"]} Goal Distribution', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.set_xlim(-0.5, 7.5)
    
    plt.suptitle(f'{result["n_simulations"]:,} Simulations', fontsize=11, color='gray')
    plt.tight_layout()
    
    filepath = f"{prefix}_goals.png" if save else None
    if save:
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {filepath}")
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return filepath


def generate_top_scores_chart(result: dict, prefix: str, save: bool, show: bool):
    """Bar chart showing most likely scorelines"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    top_scores = result['top_scores'][:8]
    n_sims = result['n_simulations']
    
    scores = [s[0] for s in top_scores]
    counts = [s[1] for s in top_scores]
    percentages = [100 * c / n_sims for c in counts]
    
    colors = []
    for score in scores:
        a, b = map(int, score.split('-'))
        if a > b:
            colors.append('#3498db')
        elif b > a:
            colors.append('#e74c3c')
        else:
            colors.append('#95a5a6')
    
    bars = ax.bar(scores, percentages, color=colors, edgecolor='white', linewidth=2)
    
    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.3, 
                f'{pct:.1f}%', ha='center', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Scoreline', fontsize=12)
    ax.set_ylabel('Probability (%)', fontsize=12)
    ax.set_title(f'Most Likely Scores: {result["team_a"]} vs {result["team_b"]}', 
                fontsize=14, fontweight='bold')
    
    legend_elements = [
        mpatches.Patch(color='#3498db', label=f'{result["team_a"]} Win'),
        mpatches.Patch(color='#95a5a6', label='Draw'),
        mpatches.Patch(color='#e74c3c', label=f'{result["team_b"]} Win'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    filepath = f"{prefix}_top_scores.png" if save else None
    if save:
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {filepath}")
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return filepath


def generate_summary_card(result: dict, prefix: str, save: bool, show: bool):
    """Visual summary card with all key information"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    team_a = result['team_a']
    team_b = result['team_b']
    
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    ax.text(0.5, 0.95, 'MUNDIALISTA-AI PREDICTION', 
            transform=ax.transAxes, ha='center', fontsize=20, 
            fontweight='bold', color='#f39c12')
    
    ax.text(0.5, 0.85, f'{team_a}  vs  {team_b}', 
            transform=ax.transAxes, ha='center', fontsize=24, 
            fontweight='bold', color='white')
    
    ax.text(0.5, 0.78, f'#{result["team_a_rank"]} ({result["team_a_points"]} pts)  |  #{result["team_b_rank"]} ({result["team_b_points"]} pts)', 
            transform=ax.transAxes, ha='center', fontsize=14, color='#aaaaaa')
    
    badge_colors = {
        'Elite Clash': '#f39c12',
        'Competitive Match': '#3498db',
        'Clear Favorite': '#9b59b6',
        'Total Mismatch': '#e74c3c',
    }
    badge_color = badge_colors.get(result['match_type'], '#3498db')
    
    ax.text(0.5, 0.72, f"{result['match_type']}", 
            transform=ax.transAxes, ha='center', fontsize=14, 
            color=badge_color, fontweight='bold')
    
    ax.text(0.20, 0.55, f"{result['team_a_win']}%", 
            transform=ax.transAxes, ha='center', fontsize=48, 
            fontweight='bold', color='#3498db')
    ax.text(0.20, 0.48, f'{team_a} Win', 
            transform=ax.transAxes, ha='center', fontsize=12, color='#aaaaaa')
    
    ax.text(0.50, 0.55, f"{result['draw']}%", 
            transform=ax.transAxes, ha='center', fontsize=48, 
            fontweight='bold', color='#95a5a6')
    ax.text(0.50, 0.48, 'Draw', 
            transform=ax.transAxes, ha='center', fontsize=12, color='#aaaaaa')
    
    ax.text(0.80, 0.55, f"{result['team_b_win']}%", 
            transform=ax.transAxes, ha='center', fontsize=48, 
            fontweight='bold', color='#e74c3c')
    ax.text(0.80, 0.48, f'{team_b} Win', 
            transform=ax.transAxes, ha='center', fontsize=12, color='#aaaaaa')
    
    ax.text(0.5, 0.38, f'Expected Goals: {result["team_a_lambda"]:.2f} - {result["team_b_lambda"]:.2f}', 
            transform=ax.transAxes, ha='center', fontsize=14, color='white')
    
    stars_a = ', '.join(result['team_a_stars'][:3]) if result['team_a_stars'] else 'No tracked stars'
    stars_b = ', '.join(result['team_b_stars'][:3]) if result['team_b_stars'] else 'No tracked stars'
    
    ax.text(0.5, 0.30, f'{team_a}: {stars_a}', 
            transform=ax.transAxes, ha='center', fontsize=11, color='#f1c40f')
    ax.text(0.5, 0.25, f'{team_b}: {stars_b}', 
            transform=ax.transAxes, ha='center', fontsize=11, color='#f1c40f')
    
    top_3 = result['top_scores'][:3]
    n_sims = result['n_simulations']
    top_scores_text = ' | '.join([f"{s[0]} ({100*s[1]/n_sims:.1f}%)" for s in top_3])
    
    ax.text(0.5, 0.16, 'Most Likely Scores:', 
            transform=ax.transAxes, ha='center', fontsize=12, 
            color='white', fontweight='bold')
    ax.text(0.5, 0.11, top_scores_text, 
            transform=ax.transAxes, ha='center', fontsize=14, color='#2ecc71')
    
    ax.text(0.5, 0.03, f'Based on {n_sims:,} Poisson simulations | {datetime.now().strftime("%Y-%m-%d %H:%M")}', 
            transform=ax.transAxes, ha='center', fontsize=10, color='#666666')
    
    plt.tight_layout()
    
    filepath = f"{prefix}_summary.png" if save else None
    if save:
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
        print(f"   Saved: {filepath}")
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return filepath


def generate_html_report(result: dict, chart_paths: dict) -> str:
    """Generate HTML report with all charts embedded"""
    
    import base64
    
    def img_to_base64(path):
        if path and os.path.exists(path):
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    
    team_a = result['team_a']
    team_b = result['team_b']
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{team_a} vs {team_b} - Mundialista-AI</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a2e; color: white; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #f39c12; text-align: center; }}
        .chart {{ margin: 20px 0; text-align: center; }}
        .chart img {{ max-width: 100%; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        .stats {{ display: flex; justify-content: space-around; padding: 20px; background: #16213e; border-radius: 10px; margin: 20px 0; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 36px; font-weight: bold; }}
        .stat-label {{ color: #aaa; }}
        .blue {{ color: #3498db; }}
        .gray {{ color: #95a5a6; }}
        .red {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{team_a} vs {team_b}</h1>
        <p style="text-align: center; color: #888;">Match Type: {result['match_type']} | Rank Gap: {result['rank_gap']}</p>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value blue">{result['team_a_win']}%</div>
                <div class="stat-label">{team_a} Win</div>
            </div>
            <div class="stat">
                <div class="stat-value gray">{result['draw']}%</div>
                <div class="stat-label">Draw</div>
            </div>
            <div class="stat">
                <div class="stat-value red">{result['team_b_win']}%</div>
                <div class="stat-label">{team_b} Win</div>
            </div>
        </div>
        
        <div class="chart">
            <img src="data:image/png;base64,{img_to_base64(chart_paths.get('summary'))}" alt="Summary">
        </div>
        
        <div class="chart">
            <img src="data:image/png;base64,{img_to_base64(chart_paths.get('probability'))}" alt="Probabilities">
        </div>
        
        <div class="chart">
            <img src="data:image/png;base64,{img_to_base64(chart_paths.get('matrix'))}" alt="Score Matrix">
        </div>
        
        <div class="chart">
            <img src="data:image/png;base64,{img_to_base64(chart_paths.get('top_scores'))}" alt="Top Scores">
        </div>
        
        <div class="chart">
            <img src="data:image/png;base64,{img_to_base64(chart_paths.get('goals'))}" alt="Goal Distribution">
        </div>
        
        <p style="text-align: center; color: #666; margin-top: 40px;">
            Generated by Mundialista-AI | {result['n_simulations']:,} simulations | {datetime.now().strftime("%Y-%m-%d %H:%M")}
        </p>
    </div>
</body>
</html>"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{OUTPUT_DIR}/{team_a}_vs_{team_b}_{timestamp}.html"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"   Saved: {filepath}")
    return filepath


if __name__ == "__main__":
    from prediction_engine import predict
    
    print("Testing chart generator...")
    result = predict("Argentina", "Brazil")
    charts = generate_all_charts(result, save=True, show=False)
    html = generate_html_report(result, charts)
    print(f"\nAll charts generated in: {OUTPUT_DIR}/")
