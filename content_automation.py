"""
Mundialista Network — Content Automation Tools
================================================
Generate social media posts, match previews, and analysis
from simulation results.

INTERACTIVE: Select teams from the full 80+ team list!
"""
import numpy as np
from collections import Counter
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# FULL TEAM DATABASE (same as app.py)
# ──────────────────────────────────────────────────────────────

TEAM_RATINGS = {
    "Brazil": 1.85, "Argentina": 1.82, "France": 1.88, "Spain": 1.78,
    "England": 1.75, "Germany": 1.70, "Portugal": 1.74, "Netherlands": 1.68,
    "Belgium": 1.65, "Italy": 1.66, "Croatia": 1.55, "Uruguay": 1.58,
    "Colombia": 1.55, "Mexico": 1.42, "USA": 1.48, "Senegal": 1.38,
    "Japan": 1.40, "South Korea": 1.35, "Australia": 1.30, "Morocco": 1.52,
    "Switzerland": 1.50, "Denmark": 1.48, "Serbia": 1.35, "Poland": 1.42,
    "Sweden": 1.35, "Chile": 1.38, "Peru": 1.30, "Ecuador": 1.42,
    "Cameroon": 1.32, "Ghana": 1.28, "Nigeria": 1.35, "Egypt": 1.30,
    "Tunisia": 1.28, "Algeria": 1.35, "Côte d'Ivoire": 1.38, "DR Congo": 1.18,
    "Mali": 1.22, "Burkina Faso": 1.18, "South Africa": 1.25,
    "Canada": 1.35, "Costa Rica": 1.22, "Panama": 1.20, "Honduras": 1.12,
    "Jamaica": 1.18, "El Salvador": 1.08, "Qatar": 1.15, "Saudi Arabia": 1.22,
    "Iran": 1.32, "Iraq": 1.18, "UAE": 1.12, "Uzbekistan": 1.15,
    "China": 1.05, "India": 0.95, "Thailand": 0.98, "Vietnam": 0.92,
    "Indonesia": 1.02, "Wales": 1.30, "Scotland": 1.25, "Republic of Ireland": 1.18,
    "Northern Ireland": 1.05, "Norway": 1.32, "Austria": 1.40, "Czech Republic": 1.32,
    "Romania": 1.18, "Hungary": 1.22, "Slovakia": 1.15, "Ukraine": 1.35,
    "Turkey": 1.42, "Greece": 1.20, "Russia": 1.30, "Paraguay": 1.25,
    "Bolivia": 1.05, "Venezuela": 1.18, "Cuba": 0.88, "Haiti": 0.85,
    "Trinidad and Tobago": 1.02, "Guatemala": 1.05, "Curaçao": 0.95,
    "New Zealand": 1.08, "Papua New Guinea": 0.65, "Fiji": 0.70,
    "New Caledonia": 0.60, "Tahiti": 0.55, "Solomon Islands": 0.58,
    "Albania": 1.18, "Georgia": 1.15, "Slovenia": 1.20, "Iceland": 1.12,
    "North Macedonia": 1.05, "Bosnia and Herzegovina": 1.22,
    "Montenegro": 1.08, "Luxembourg": 0.82, "Bahrain": 1.02,
}

# ──────────────────────────────────────────────────────────────
# QUICK SIMULATION ENGINE (lightweight version for content gen)
# ──────────────────────────────────────────────────────────────

def quick_simulate(home_team, away_team, n_sims=10200):
    """Run a quick Poisson simulation for content generation."""
    home_rate = TEAM_RATINGS.get(home_team, 1.10)
    away_rate = TEAM_RATINGS.get(away_team, 1.10)
    
    # Home advantage
    home_lambda = home_rate * 1.12
    away_lambda = away_rate * 0.88
    
    # Simulate
    home_goals = np.random.poisson(home_lambda, n_sims)
    away_goals = np.random.poisson(away_lambda, n_sims)
    
    # Analytics
    home_wins = np.sum(home_goals > away_goals)
    draws = np.sum(home_goals == away_goals)
    away_wins = np.sum(home_goals < away_goals)
    
    # Top scorelines
    scorelines = list(zip(home_goals, away_goals))
    score_counts = Counter(scorelines)
    top5 = score_counts.most_common(5)
    
    # Determine favourite/underdog
    if home_rate >= away_rate:
        favourite, underdog = home_team, away_team
        upset_prob = away_wins / n_sims * 100
    else:
        favourite, underdog = away_team, home_team
        upset_prob = home_wins / n_sims * 100
    
    analytics = {
        "home_win_pct": home_wins / n_sims * 100,
        "draw_pct": draws / n_sims * 100,
        "away_win_pct": away_wins / n_sims * 100,
        "home_exp": np.mean(home_goals),
        "away_exp": np.mean(away_goals),
        "top5_scorelines": top5,
        "upset_prob": upset_prob,
        "favourite": favourite,
        "underdog": underdog,
        "n": n_sims,
    }
    
    return analytics


# ──────────────────────────────────────────────────────────────
# CONTENT GENERATORS
# ──────────────────────────────────────────────────────────────

def generate_match_preview(home_team, away_team, analytics):
    """Generate a match preview post for social media."""
    hw = analytics["home_win_pct"]
    dr = analytics["draw_pct"]
    aw = analytics["away_win_pct"]
    home_xg = analytics["home_exp"]
    away_xg = analytics["away_exp"]
    top_score = analytics["top5_scorelines"][0]
    upset = analytics["upset_prob"]
    
    preview = f"""⚽ MATCH PREDICTION | {home_team} vs {away_team}
🏟️ Powered by Mundialista Network AI | 10,200 Simulations

📊 WIN PROBABILITIES:
🏠 {home_team}: {hw:.1f}%
🤝 Draw: {dr:.1f}%
✈️ {away_team}: {aw:.1f}%

⚽ EXPECTED GOALS:
{home_team}: {home_xg:.2f} xG
{away_team}: {away_xg:.2f} xG

🎯 MOST LIKELY SCORE: {home_team} {top_score[0][0]} - {top_score[0][1]} {away_team} ({top_score[1]/analytics['n']*100:.1f}%)

🔥 UPSET PROBABILITY: {upset:.1f}%

#WorldCup2026 #WC2026 #MundialistaNetwork #NuestraIA"""
    
    return preview


def generate_twitter_thread(home_team, away_team, analytics):
    """Generate a Twitter/X thread from simulation results."""
    hw = analytics["home_win_pct"]
    dr = analytics["draw_pct"]
    aw = analytics["away_win_pct"]
    home_xg = analytics["home_exp"]
    away_xg = analytics["away_exp"]
    upset = analytics["upset_prob"]
    fav = analytics["favourite"]
    dog = analytics["underdog"]
    
    thread = []
    
    thread.append(f"""🧵 THREAD: {home_team} vs {away_team} — AI PREDICTION

Our engine just ran 10,200 simulations. Here's what it found 👇

#WorldCup2026 #MundialistaNetwork""")
    
    if hw > aw and hw > dr:
        winner_emoji = "🏠"
        winner = home_team
    elif aw > hw and aw > dr:
        winner_emoji = "✈️"
        winner = away_team
    else:
        winner_emoji = "🤝"
        winner = "DRAW"
    
    thread.append(f"""📊 THE NUMBERS:

{winner_emoji} Our AI favors: {winner}

🏠 {home_team}: {hw:.1f}%
🤝 Draw: {dr:.1f}%
✈️ {away_team}: {aw:.1f}%

Based on Bayesian inference + 10,200 Poisson simulations.""")
    
    scores_text = ""
    for (h, a), cnt in analytics["top5_scorelines"][:3]:
        pct = cnt / analytics["n"] * 100
        scores_text += f"\n{home_team} {h}-{a} {away_team}: {pct:.1f}%"
    
    thread.append(f"""🎯 MOST LIKELY SCORELINES:
{scores_text}

⚽ Expected Goals:
{home_team}: {home_xg:.2f} xG
{away_team}: {away_xg:.2f} xG""")
    
    if upset > 30:
        alert = "⚠️ HIGH UPSET POTENTIAL"
    elif upset > 20:
        alert = "👀 MODERATE UPSET CHANCE"
    else:
        alert = "📉 LOW UPSET PROBABILITY"
    
    thread.append(f"""🔥 UPSET WATCH:

{alert}

{dog} has a {upset:.1f}% chance of pulling off the upset against {fav}.

{'This could be a HUGE shock! 😱' if upset > 30 else 'The favorite should handle this, but football is unpredictable! ⚽'}""")
    
    thread.append(f"""💡 Want to run your own predictions?

Try our free AI engine:
🔗 https://mundialista-ai-8sya4tqzo7fyi65rqgwonw.streamlit.app

It works with 80+ national teams and runs 10,200 simulations per match!

Follow @MundialistaNet for daily WC2026 predictions 🌍⚽

#WC2026 #FootballPredictions #AI""")
    
    return thread


def generate_spanish_preview(home_team, away_team, analytics):
    """Generate a Spanish language match preview."""
    hw = analytics["home_win_pct"]
    dr = analytics["draw_pct"]
    aw = analytics["away_win_pct"]
    home_xg = analytics["home_exp"]
    away_xg = analytics["away_exp"]
    top_score = analytics["top5_scorelines"][0]
    upset = analytics["upset_prob"]
    
    preview = f"""⚽ PREDICCIÓN | {home_team} vs {away_team}
🏟️ Mundialista Network AI | 10,200 Simulaciones

📊 PROBABILIDADES:
🏠 {home_team}: {hw:.1f}%
🤝 Empate: {dr:.1f}%
✈️ {away_team}: {aw:.1f}%

⚽ GOLES ESPERADOS:
{home_team}: {home_xg:.2f} xG
{away_team}: {away_xg:.2f} xG

🎯 MARCADOR MÁS PROBABLE: {home_team} {top_score[0][0]} - {top_score[0][1]} {away_team} ({top_score[1]/analytics['n']*100:.1f}%)

🔥 PROBABILIDAD DE SORPRESA: {upset:.1f}%

#Mundial2026 #WC2026 #MundialistaNetwork #NuestraIA"""
    
    return preview


def generate_underdog_alert(home_team, away_team, analytics):
    """Generate an underdog alert if upset probability is high."""
    upset = analytics["upset_prob"]
    dog = analytics["underdog"]
    fav = analytics["favourite"]
    
    if upset < 25:
        return None
    
    if upset > 40:
        level = "🚨🚨🚨 MAXIMUM ALERT"
        emoji = "😱"
    elif upset > 30:
        level = "🚨🚨 HIGH ALERT"
        emoji = "👀"
    else:
        level = "🚨 ALERT"
        emoji = "⚡"
    
    alert = f"""{level} — UNDERDOG WATCH {emoji}

{dog} has a {upset:.1f}% chance of UPSETTING {fav}!

{'This is basically a coin flip! Anything can happen! 🪙' if upset > 40 else f'{dog} is a real threat here. Do not sleep on them! 💪'}

📊 Full analysis: https://mundialista-ai-8sya4tqzo7fyi65rqgwonw.streamlit.app

#WorldCup2026 #Underdog #WC2026 #MundialistaNetwork"""
    
    return alert


# ──────────────────────────────────────────────────────────────
# INTERACTIVE TEAM SELECTOR
# ──────────────────────────────────────────────────────────────

def show_teams():
    """Display all available teams."""
    teams = sorted(TEAM_RATINGS.keys())
    print("\n⚽ AVAILABLE TEAMS ({} total):".format(len(teams)))
    print("=" * 60)
    for i, team in enumerate(teams, 1):
        rating = TEAM_RATINGS[team]
        stars = "⭐" * min(5, max(1, int(rating / 0.4)))
        print(f"  {i:3d}. {team:<30s} ({rating:.2f}) {stars}")
    print("=" * 60)


def select_team(prompt):
    """Let user select a team by name or number."""
    teams = sorted(TEAM_RATINGS.keys())
    while True:
        choice = input(prompt).strip()
        
        # Check if they entered a number
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(teams):
                return teams[idx]
            else:
                print(f"  ❌ Enter a number between 1 and {len(teams)}")
                continue
        except ValueError:
            pass
        
        # Check if they typed a team name (fuzzy match)
        matches = [t for t in teams if choice.lower() in t.lower()]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print(f"  Multiple matches found:")
            for m in matches:
                print(f"    - {m}")
            print(f"  Please be more specific.")
        else:
            print(f"  ❌ Team '{choice}' not found. Try again or enter a number.")


def interactive_menu():
    """Main interactive menu."""
    print("""
╔══════════════════════════════════════════════════════════╗
║        ⚽ MUNDIALISTA NETWORK — CONTENT GENERATOR ⚽     ║
║        Powered by AI | 10,200 Simulations                ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n📋 MENU:")
        print("  1. 📊 Generate Match Preview (English)")
        print("  2. 📊 Generate Match Preview (Spanish)")
        print("  3. 🧵 Generate Twitter/X Thread")
        print("  4. 🔥 Check Underdog Alert")
        print("  5. 📋 Show All Teams")
        print("  6. 🚪 Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "6":
            print("\n👋 ¡Hasta la vista! Follow @MundialistaNet ⚽")
            break
        
        if choice == "5":
            show_teams()
            continue
        
        if choice in ["1", "2", "3", "4"]:
            print("\n🏟️ SELECT TEAMS:")
            show_teams()
            
            home = select_team("\n🏠 Home team (name or number): ")
            away = select_team("✈️  Away team (name or number): ")
            
            print(f"\n⏳ Running 10,200 simulations: {home} vs {away}...")
            analytics = quick_simulate(home, away)
            
            if choice == "1":
                print("\n" + "=" * 60)
                print("📋 ENGLISH PREVIEW — Copy & Paste Ready:")
                print("=" * 60)
                print(generate_match_preview(home, away, analytics))
                
            elif choice == "2":
                print("\n" + "=" * 60)
                print("📋 SPANISH PREVIEW — Listo para copiar y pegar:")
                print("=" * 60)
                print(generate_spanish_preview(home, away, analytics))
                
            elif choice == "3":
                print("\n" + "=" * 60)
                print("🧵 TWITTER THREAD — Post each tweet separately:")
                print("=" * 60)
                thread = generate_twitter_thread(home, away, analytics)
                for i, tweet in enumerate(thread, 1):
                    print(f"\n{'─' * 40}")
                    print(f"📝 Tweet {i}/{len(thread)}:")
                    print(f"{'─' * 40}")
                    print(tweet)
                
            elif choice == "4":
                alert = generate_underdog_alert(home, away, analytics)
                print("\n" + "=" * 60)
                if alert:
                    print("🚨 UNDERDOG ALERT GENERATED:")
                    print("=" * 60)
                    print(alert)
                else:
                    print(f"✅ No upset alert — {analytics['favourite']} is a clear favorite.")
                    print(f"   Upset probability: only {analytics['upset_prob']:.1f}%")
                    print("=" * 60)
            
            print("\n✅ Content generated! Copy the text above for your post.")
        
        else:
            print("❌ Invalid option. Enter 1-6.")


# ──────────────────────────────────────────────────────────────
# RUN
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    interactive_menu()