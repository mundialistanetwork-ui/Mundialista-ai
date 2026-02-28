"""
Mundialista Network — GPT4All Content Amplifier Agent
======================================================
Generates bilingual match summaries, blog previews,
and social media posts using LOCAL AI (no API costs).

Requires: GPT4All installed with a downloaded model.
"""

from gpt4all import GPT4All
import json
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────

# Change this to whatever model you downloaded in GPT4All
MODEL_NAME = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"

print("⏳ Loading GPT4All model... (first time may take a minute)")
try:
    model = GPT4All(MODEL_NAME)
    print("✅ Model loaded successfully!\n")
except Exception as e:
    print(f"❌ Could not load model: {e}")
    print("Make sure you've downloaded a model in GPT4All Desktop app.")
    print("Available models will be in: C:\\Users\\bayen\\AppData\\Local\\nomic.ai\\GPT4All\\")
    print("\nTrying alternative model names...")
    
    # Try common model names
    alternatives = [
        "Meta-Llama-3-8B-Instruct.Q4_0.gguf",
        "mistral-7b-instruct-v0.2.Q4_0.gguf",
        "gpt4all-falcon-newbpe-q4_0.gguf",
        "orca-mini-3b-gguf2-q4_0.gguf",
    ]
    
    model = None
    for alt in alternatives:
        try:
            print(f"  Trying {alt}...")
            model = GPT4All(alt)
            print(f"  ✅ Loaded: {alt}")
            MODEL_NAME = alt
            break
        except:
            continue
    
    if model is None:
        print("\n❌ No model found. Please open GPT4All desktop app and download a model first.")
        print("Then update MODEL_NAME in this script.")
        exit(1)


# ──────────────────────────────────────────────────────────────
# TEAM DATABASE
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
    "New Zealand": 1.08, "Albania": 1.18, "Georgia": 1.15, "Slovenia": 1.20,
}


# ──────────────────────────────────────────────────────────────
# CONTENT GENERATORS
# ──────────────────────────────────────────────────────────────

def generate_match_summary(home_team, away_team, home_goals, away_goals, language="both"):
    """Generate AI-written match summary."""
    
    if home_goals > away_goals:
        result = f"{home_team} won"
        result_es = f"{home_team} ganó"
    elif away_goals > home_goals:
        result = f"{away_team} won"
        result_es = f"{away_team} ganó"
    else:
        result = "The match ended in a draw"
        result_es = "El partido terminó en empate"
    
    prompt_en = f"""You are a professional football journalist for Mundialista Network covering World Cup 2026.

Write a 150-word match recap for:
{home_team} {home_goals} - {away_goals} {away_team}

Result: {result}
Competition: FIFA World Cup 2026

The recap should be:
- Exciting and fan-friendly
- Include tactical observations
- Mention the significance of the result
- End with what this means for both teams going forward

Write ONLY the recap, no title needed."""

    prompt_es = f"""Eres un periodista deportivo profesional de Mundialista Network cubriendo el Mundial 2026.

Escribe un resumen del partido de 150 palabras:
{home_team} {home_goals} - {away_goals} {away_team}

Resultado: {result_es}
Competición: Copa Mundial FIFA 2026

El resumen debe ser:
- Emocionante y cercano al aficionado
- Incluir observaciones tácticas
- Mencionar la importancia del resultado
- Terminar con lo que significa para ambos equipos

Escribe SOLO el resumen, sin título."""

    results = {}
    
    if language in ["en", "both"]:
        print("  ⏳ Generating English summary...")
        with model.chat_session():
            results["english"] = model.generate(prompt_en, max_tokens=400, temp=0.7)
    
    if language in ["es", "both"]:
        print("  ⏳ Generating Spanish summary...")
        with model.chat_session():
            results["spanish"] = model.generate(prompt_es, max_tokens=400, temp=0.7)
    
    return results


def generate_blog_preview(home_team, away_team):
    """Generate a full blog preview post."""
    
    home_rating = TEAM_RATINGS.get(home_team, 1.10)
    away_rating = TEAM_RATINGS.get(away_team, 1.10)
    
    if home_rating > away_rating:
        favorite = home_team
        underdog = away_team
    else:
        favorite = away_team
        underdog = home_team
    
    prompt = f"""You are the lead analyst for Mundialista Network, covering FIFA World Cup 2026.

Write a 500-word match preview blog post for:
{home_team} vs {away_team}

Structure:
## Team Form
Discuss both teams' recent trajectory and World Cup history.

## Key Players to Watch
Name 2-3 key players from each side and why they matter.

## Tactical Notes
How might each team set up? What tactical battle will decide this match?

## Prediction
Give a predicted scoreline with reasoning.

Important:
- {favorite} is the slight favorite based on our AI ratings
- {underdog} is the underdog but has potential
- Be engaging, use football knowledge
- This is for World Cup 2026 in USA, Mexico, and Canada
- End with: "Run your own simulation at Mundialista Network AI"

Write the full blog post now."""

    print("  ⏳ Generating blog preview (this takes ~30 seconds)...")
    with model.chat_session():
        english = model.generate(prompt, max_tokens=1000, temp=0.7)
    
    prompt_es = f"""Eres el analista principal de Mundialista Network, cubriendo la Copa Mundial FIFA 2026.

Escribe una vista previa del partido de 500 palabras en formato blog:
{home_team} vs {away_team}

Estructura:
## Forma de los Equipos
## Jugadores Clave
## Notas Tácticas  
## Predicción

- {favorite} es el ligero favorito
- {underdog} es la sorpresa potencial
- Mundial 2026 en USA, México y Canadá
- Termina con: "Ejecuta tu propia simulación en Mundialista Network AI"

Escribe el artículo completo ahora."""

    print("  ⏳ Generating Spanish version...")
    with model.chat_session():
        spanish = model.generate(prompt_es, max_tokens=1000, temp=0.7)
    
    return {"english": english, "spanish": spanish}


def generate_social_posts(home_team, away_team, post_type="preview"):
    """Generate social media posts for multiple platforms."""
    
    prompts = {
        "twitter": f"""Write a fun, exciting tweet (max 280 characters) for a World Cup 2026 match preview: {home_team} vs {away_team}. Include 2 relevant hashtags. Include an emoji. Write in English.""",
        
        "twitter_es": f"""Escribe un tweet divertido y emocionante (máximo 280 caracteres) para una vista previa del Mundial 2026: {home_team} vs {away_team}. Incluye 2 hashtags relevantes y un emoji. Escribe en español.""",
        
        "instagram": f"""Write an Instagram caption (2-3 sentences) for a World Cup 2026 match preview post: {home_team} vs {away_team}. Make it engaging with emojis. Add 5 hashtags at the end. Include a call to action: "Link in bio for AI predictions 🤖".""",
        
        "tiktok": f"""Write a short, punchy TikTok caption (1-2 sentences, max 150 characters) for a World Cup 2026 prediction video: {home_team} vs {away_team}. Make it viral-worthy with emojis. Add 3 hashtags.""",
    }
    
    results = {}
    for platform, prompt in prompts.items():
        print(f"  ⏳ Generating {platform} post...")
        with model.chat_session():
            results[platform] = model.generate(prompt, max_tokens=200, temp=0.8)
    
    return results


# ──────────────────────────────────────────────────────────────
# TEAM SELECTOR
# ──────────────────────────────────────────────────────────────

def show_teams():
    """Display all available teams."""
    teams = sorted(TEAM_RATINGS.keys())
    print(f"\n⚽ AVAILABLE TEAMS ({len(teams)} total):")
    print("=" * 60)
    for i, team in enumerate(teams, 1):
        print(f"  {i:3d}. {team:<30s} ({TEAM_RATINGS[team]:.2f})")
    print("=" * 60)


def select_team(prompt):
    """Let user select a team by name or number."""
    teams = sorted(TEAM_RATINGS.keys())
    while True:
        choice = input(prompt).strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(teams):
                return teams[idx]
        except ValueError:
            pass
        matches = [t for t in teams if choice.lower() in t.lower()]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print(f"  Multiple matches: {', '.join(matches)}")
        else:
            print(f"  ❌ Not found. Try again.")


# ──────────────────────────────────────────────────────────────
# INTERACTIVE MENU
# ──────────────────────────────────────────────────────────────

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║   ⚽ MUNDIALISTA NETWORK — GPT4All CONTENT AMPLIFIER ⚽      ║
║   Local AI • No API Costs • Bilingual Content                ║
║   Model: """ + MODEL_NAME + """
╚══════════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n📋 CONTENT MENU:")
        print("  1. 📝 Match Summary (post-match recap)")
        print("  2. 📰 Blog Preview (500-word preview)")
        print("  3. 📱 Social Media Posts (X, Instagram, TikTok)")
        print("  4. 🌍 Full Content Package (all of the above)")
        print("  5. 📋 Show All Teams")
        print("  6. 🚪 Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "6":
            print("\n👋 ¡Hasta la victoria! — Mundialista Network ⚽")
            break
        
        if choice == "5":
            show_teams()
            continue
        
        if choice in ["1", "2", "3", "4"]:
            print("\n🏟️ SELECT TEAMS:")
            show_teams()
            home = select_team("\n🏠 Home team: ")
            away = select_team("✈️  Away team: ")
            print(f"\n🎯 {home} vs {away}")
            
            # ── Match Summary ──
            if choice in ["1", "4"]:
                if choice == "1":
                    home_g = input(f"⚽ {home} goals: ").strip()
                    away_g = input(f"⚽ {away} goals: ").strip()
                else:
                    home_g = input(f"⚽ {home} goals (or press Enter to skip summary): ").strip()
                    away_g = input(f"⚽ {away} goals: ").strip() if home_g else ""
                
                if home_g and away_g:
                    summaries = generate_match_summary(home, away, int(home_g), int(away_g))
                    print("\n" + "=" * 60)
                    print("📝 MATCH SUMMARY — ENGLISH:")
                    print("=" * 60)
                    print(summaries.get("english", ""))
                    print("\n" + "=" * 60)
                    print("📝 RESUMEN DEL PARTIDO — ESPAÑOL:")
                    print("=" * 60)
                    print(summaries.get("spanish", ""))
            
            # ── Blog Preview ──
            if choice in ["2", "4"]:
                blog = generate_blog_preview(home, away)
                print("\n" + "=" * 60)
                print("📰 BLOG PREVIEW — ENGLISH:")
                print("=" * 60)
                print(blog["english"])
                print("\n" + "=" * 60)
                print("📰 VISTA PREVIA — ESPAÑOL:")
                print("=" * 60)
                print(blog["spanish"])
            
            # ── Social Media ──
            if choice in ["3", "4"]:
                posts = generate_social_posts(home, away)
                print("\n" + "=" * 60)
                print("📱 SOCIAL MEDIA POSTS:")
                print("=" * 60)
                for platform, content in posts.items():
                    print(f"\n{'─' * 40}")
                    print(f"📌 {platform.upper()}:")
                    print(f"{'─' * 40}")
                    print(content)
            
            print("\n✅ Content generated! Copy and paste where needed.")
            
            # Save option
            save = input("\n💾 Save to file? (y/n): ").strip().lower()
            if save == "y":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"content_{home}_{away}_{timestamp}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"Mundialista Network Content — {home} vs {away}\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write("[ Content saved from interactive session ]\n")
                print(f"  ✅ Saved to: {filename}")
        
        else:
            print("❌ Invalid option.")


if __name__ == "__main__":
    main()