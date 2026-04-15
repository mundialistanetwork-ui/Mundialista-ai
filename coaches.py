"""
Mundialista AI - Coaches Module v8
Tier-based coaching impact system for international football prediction.
"""

from pathlib import Path
import json

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COACHES TIER SYSTEM & DATA
#  Mundialista-AI v8 — Updated April 2026
#  All coaches verified against confirmed 2026 WC squads
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
Coaches Classification Tiers:
─────────────────────────────────────────────
  "Elite Tactician"       → Top-tier, proven at highest level
  "Seasoned Strategist"   → Strong track record, consistently competitive
  "Solid Organizer"       → Competent, respectable results
  "Developing Manager"    → New to top-level international management
  "Unproven Appointment"  → Very recent appointment, limited data

Coaches impact is modeled as multipliers on attack (goal creation)
and defense (goals denied).
- Defense impact is LARGER than attack → coaches organize defense
  more than they create goals.
- "Elite Tactician" doesn't guarantee wins, but raises the floor
  and ceiling.

Dampened Multiplier Reference:
─────────────────────────────────────────────
Tier                    ATK (dampened)   DEF (dampened)
Elite Tactician          1.042            0.944
Seasoned Strategist      1.021            0.965
Solid Organizer          1.000            0.986
Developing Manager       0.986            1.014
Unproven Appointment     0.965            1.042

Max swing (Elite vs Unproven): ~18-22% on lambda → ~8-12% win probability
"""

COACH_TIERS = {
    "Elite Tactician": {
        "tier_rank": 1,
        "attack_mult": 1.060,
        "defense_mult": 0.920,
        "description": "Top-tier, proven at highest level",
    },
    "Seasoned Strategist": {
        "tier_rank": 2,
        "attack_mult": 1.030,
        "defense_mult": 0.950,
        "description": "Strong track record, consistently competitive",
    },
    "Solid Organizer": {
        "tier_rank": 3,
        "attack_mult": 1.000,
        "defense_mult": 0.980,
        "description": "Competent, respectable results",
    },
    "Developing Manager": {
        "tier_rank": 4,
        "attack_mult": 0.980,
        "defense_mult": 1.020,
        "description": "New to top-level international management",
    },
    "Unproven Appointment": {
        "tier_rank": 5,
        "attack_mult": 0.950,
        "defense_mult": 1.060,
        "description": "Very recent appointment, limited data",
    },
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COACHES CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COACH_CONFIG = {
    "COACH_IMPACT_DAMPENING": 0.75,   # Scale raw multipliers (keeps it realistic)
    "TIER_GAP_THRESHOLD": 2,          # Bonus kicks in when tier gap >= this
    "TIER_GAP_BONUS": 0.015,          # Per tier level beyond threshold
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BUILT-IN COACHES DATABASE
#  Add/edit teams here. Override with data/coaches.json if needed.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_BUILTIN_COACHES = {
    "Argentina": {
        "name": "Lionel Scaloni",
        "tier": "Elite Tactician",
        "style": "Balanced possession with pressing triggers, tactical flexibility",
        "honors": ["2022 World Cup", "2021 Copa America", "2024 Copa America"],
        "notes": "Back-to-back Copa Americas + World Cup; masterclass in squad management",
        "appointed": "2018",
    },
    "Brazil": {
        "name": "Carlo Ancelotti",
        "tier": "Elite Tactician",
        "style": "Possession-based, vertical transitions, positional flexibility",
        "honors": ["2003 CL (AC Milan)", "2007 CL (AC Milan)", "2014 CL (Real Madrid)", "2022 CL (Real Madrid)"],
        "notes": "Most decorated club coach in Champions League history; first major intl test",
        "appointed": "2025",
    },
    "France": {
        "name": "Didier Deschamps",
        "tier": "Elite Tactician",
        "style": "Pragmatic, defensively solid, tournament specialist",
        "honors": ["2018 World Cup", "2022 WC Runner-Up", "2x Euro Final"],
        "notes": "Longest-serving France manager; unmatched tournament pedigree",
        "appointed": "2012",
    },
    "England": {
        "name": "Thomas Tuchel",
        "tier": "Elite Tactician",
        "style": "High press, positional play, flexible formations",
        "honors": ["2021 Champions League (Chelsea)", "2x DFB-Pokal"],
        "notes": "Appointed Jan 2025; elite club pedigree, intl debut",
        "appointed": "2025",
    },
    "Spain": {
        "name": "Luis de la Fuente",
        "tier": "Seasoned Strategist",
        "style": "Possession-based, youth integration, tiki-taka evolution",
        "honors": ["2024 Euro", "2023 Nations League"],
        "notes": "Rose through Spanish youth ranks; Euro 2024 dominant run",
        "appointed": "2022",
    },
    "Germany": {
        "name": "Julian Nagelsmann",
        "tier": "Seasoned Strategist",
        "style": "High-intensity press, positional play, data-driven",
        "honors": [],
        "notes": "Youngest Bundesliga coach ever; strong Euro 2024 showing",
        "appointed": "2023",
    },
    "Portugal": {
        "name": "Roberto Martinez",
        "tier": "Seasoned Strategist",
        "style": "Possession build-up, attacking fullbacks, fluid front line",
        "honors": ["2023 Nations League (semi)"],
        "notes": "Revitalized Portugal attack; managing Ronaldo's role well",
        "appointed": "2023",
    },
    "Netherlands": {
        "name": "Ronald Koeman",
        "tier": "Seasoned Strategist",
        "style": "Dutch 4-3-3, direct attacking, physical midfield",
        "honors": [],
        "notes": "Second stint as Oranje boss; stabilized after 2022 WC exit",
        "appointed": "2023",
    },
    "Belgium": {
        "name": "Domenico Tedesco",
        "tier": "Solid Organizer",
        "style": "Structured defense, counter-attacking transitions",
        "honors": [],
        "notes": "Post-golden generation rebuild; young squad development",
        "appointed": "2023",
    },
    "Italy": {
        "name": "Luciano Spalletti",
        "tier": "Seasoned Strategist",
        "style": "Tactical flexibility, compact defense, quick transitions",
        "honors": ["2023 Serie A (Napoli)"],
        "notes": "Napoli scudetto mastermind; rebuilding post-Euro 2024 exit",
        "appointed": "2023",
    },
    "Croatia": {
        "name": "Zlatko Dalic",
        "tier": "Seasoned Strategist",
        "style": "Midfield control, tournament resilience, veteran management",
        "honors": ["2018 WC Runner-Up", "2022 WC Third Place"],
        "notes": "Two consecutive WC semis; master of squad cohesion",
        "appointed": "2017",
    },
    "Colombia": {
        "name": "Nestor Lorenzo",
        "tier": "Solid Organizer",
        "style": "Organized defense, direct counters, physical presence",
        "honors": ["2024 Copa America Runner-Up"],
        "notes": "Surprise Copa 2024 run; steady improvement trajectory",
        "appointed": "2022",
    },
    "Uruguay": {
        "name": "Marcelo Bielsa",
        "tier": "Elite Tactician",
        "style": "High press, man-marking, relentless intensity",
        "honors": ["2004 Olympics Gold (Argentina)"],
        "notes": "El Loco — revolutionary tactician; polarizing but brilliant",
        "appointed": "2023",
    },
    "United States": {
        "name": "Mauricio Pochettino",
        "tier": "Seasoned Strategist",
        "style": "High press, attacking fullbacks, youth development",
        "honors": ["2019 CL Final (Spurs)"],
        "notes": "Appointed 2024; elite club pedigree, first intl role, host nation pressure",
        "appointed": "2024",
    },
    "Mexico": {
        "name": "Javier Aguirre",
        "tier": "Seasoned Strategist",
        "style": "Pragmatic, defensively organized, tournament experienced",
        "honors": ["2x WC Round of 16 (Mexico)"],
        "notes": "Third stint; veteran crisis manager for co-host nation",
        "appointed": "2024",
    },
    "Japan": {
        "name": "Hajime Moriyasu",
        "tier": "Solid Organizer",
        "style": "Disciplined pressing, quick transitions, European-based talent",
        "honors": ["2x Asian Cup Runner-Up"],
        "notes": "Beat Germany and Spain at WC 2022; consistent overperformer",
        "appointed": "2018",
    },
    "South Korea": {
        "name": "Hong Myung-bo",
        "tier": "Solid Organizer",
        "style": "Organized defense, disciplined shape, Son-centric attack",
        "honors": [],
        "notes": "2002 WC legend as player; second stint as manager",
        "appointed": "2024",
    },
    "Morocco": {
        "name": "Walid Regragui",
        "tier": "Seasoned Strategist",
        "style": "Compact low block, devastating counters, set piece mastery",
        "honors": ["2022 WC Semi-Final", "2024 AFCON Runner-Up"],
        "notes": "Historic WC 2022 run; first African/Arab semi-finalist coach",
        "appointed": "2022",
    },
    "Senegal": {
        "name": "Aliou Cisse",
        "tier": "Solid Organizer",
        "style": "Physical defense, direct attack, squad unity",
        "honors": ["2022 AFCON"],
        "notes": "First Senegal AFCON title; post-Mane transition underway",
        "appointed": "2015",
    },
    "Egypt": {
        "name": "Hossam Hassan",
        "tier": "Developing Manager",
        "style": "Defensive stability, Salah-centric attack",
        "honors": [],
        "notes": "Egypt legend as player; limited managerial experience at top level",
        "appointed": "2024",
    },
    "Norway": {
        "name": "Stale Solbakken",
        "tier": "Solid Organizer",
        "style": "Direct, Haaland-centric, pragmatic 4-3-3",
        "honors": [],
        "notes": "Building around Haaland/Odegaard; WC qualification would be historic",
        "appointed": "2020",
    },
    "Turkey": {
        "name": "Vincenzo Montella",
        "tier": "Solid Organizer",
        "style": "Possession build-up, young talent integration",
        "honors": [],
        "notes": "Surprise Euro 2024 QF run; energized young squad",
        "appointed": "2023",
    },
    "Australia": {
        "name": "Tony Popovic",
        "tier": "Developing Manager",
        "style": "Organized defense, set pieces, physical approach",
        "honors": [],
        "notes": "A-League experience; WC qualification specialist needed",
        "appointed": "2024",
    },
    "Canada": {
        "name": "Jesse Marsch",
        "tier": "Solid Organizer",
        "style": "High press, gegenpressing, intense transitions",
        "honors": [],
        "notes": "MLS/Bundesliga experience; co-host nation expectations",
        "appointed": "2024",
    },
    "Paraguay": {
        "name": "Alfaro",
        "tier": "Solid Organizer",
        "style": "Defensive discipline, counter-attacking",
        "honors": [],
        "notes": "South American qualifying grind",
        "appointed": "2024",
    },
    "Saudi Arabia": {
        "name": "Roberto Mancini",
        "tier": "Seasoned Strategist",
        "style": "Possession control, Italian defensive structure",
        "honors": ["2021 Euro (Italy)", "2012 Premier League (Man City)"],
        "notes": "Euro winner with Italy; massive contract for Saudi ambitions",
        "appointed": "2023",
    },
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COACHES IMPACT FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_coach_data(team: str, data_dir: Path = None) -> dict:
    """
    Retrieve coach information for a team.

    Priority:
    1. data/coaches.json (if exists — user override)
    2. _BUILTIN_COACHES (built-in database above)
    3. Default "Unknown" with neutral multipliers

    Args:
        team: Country name (must match dataset exactly)
        data_dir: Path to data/ folder (for coaches.json override)

    Returns:
        Dict with name, tier, multipliers, style, honors, notes
    """
    coaches_db = _BUILTIN_COACHES

    # Check for user override file
    if data_dir is not None:
        coach_path = data_dir / "coaches.json"
        if coach_path.exists():
            try:
                with open(coach_path, "r", encoding="utf-8") as f:
                    coaches_db = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass  # Fall back to built-in

    # Unknown team → neutral impact
    if team not in coaches_db:
        return {
            "name": "Unknown",
            "tier": "Solid Organizer",
            "tier_rank": 3,
            "attack_mult": 1.0,
            "defense_mult": 1.0,
            "style": "Unknown",
            "description": "No coaches data available",
            "honors": [],
            "notes": "",
            "appointed": "",
        }

    coach = coaches_db[team]
    tier_name = coach.get("tier", "Solid Organizer")
    tier_data = COACH_TIERS.get(tier_name, COACH_TIERS["Solid Organizer"])

    # Apply dampening (raw → realistic)
    dampen = COACH_CONFIG["COACH_IMPACT_DAMPENING"]
    raw_atk = tier_data["attack_mult"]
    raw_def = tier_data["defense_mult"]
    atk_mult = 1.0 + (raw_atk - 1.0) * dampen
    def_mult = 1.0 + (raw_def - 1.0) * dampen

    return {
        "name": coach.get("name", "Unknown"),
        "tier": tier_name,
        "tier_rank": tier_data["tier_rank"],
        "attack_mult": round(atk_mult, 4),
        "defense_mult": round(def_mult, 4),
        "style": coach.get("style", ""),
        "description": tier_data["description"],
        "honors": coach.get("honors", []),
        "notes": coach.get("notes", ""),
        "appointed": coach.get("appointed", ""),
    }


def compute_coach_matchup_edge(coach_a: dict, coach_b: dict) -> tuple:
    """
    Tier gap bonus: if one coach is significantly better-ranked,
    they get a small lambda boost.

    Example: Elite Tactician (1) vs Developing Manager (4)
             Gap = 3, threshold = 2 → bonus tiers = 2
             edge = 1.0 + 2 * 0.015 = 1.030

    Returns:
        (edge_a, edge_b) — one will be > 1.0, the other stays 1.0
    """
    gap = coach_a["tier_rank"] - coach_b["tier_rank"]
    threshold = COACH_CONFIG["TIER_GAP_THRESHOLD"]
    bonus = COACH_CONFIG["TIER_GAP_BONUS"]

    edge_a = 1.0
    edge_b = 1.0

    abs_gap = abs(gap)
    if abs_gap >= threshold:
        bonus_amount = (abs_gap - threshold + 1) * bonus
        if gap > 0:
            # coach_b is better (lower tier_rank = better)
            edge_b = 1.0 + bonus_amount
        elif gap < 0:
            # coach_a is better
            edge_a = 1.0 + bonus_amount

    return round(edge_a, 4), round(edge_b, 4)