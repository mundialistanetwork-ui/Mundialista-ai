def _format_scoreline_entry(sc) -> str:
    """Format a top scoreline entry safely."""
    if not isinstance(sc, (list, tuple)) or len(sc) < 2:
        return "N/A"

    raw_score, pct = sc[0], sc[1]

    if isinstance(raw_score, (list, tuple)) and len(raw_score) == 2:
        score_str = f"{raw_score[0]}-{raw_score[1]}"
    else:
        score_str = str(raw_score)

    if isinstance(pct, (int, float)):
        if pct < 1:
            pct *= 100
        return f"{score_str} ({pct:.1f}%)"

    return score_str


def _winner_name(home: str, away: str, a: dict) -> str:
    """Return the most likely outcome label."""
    hw, dr, aw = a["home_win_pct"], a["draw_pct"], a["away_win_pct"]
    if hw >= dr and hw >= aw:
        return home
    elif aw >= hw and aw >= dr:
        return away
    return "Draw"


def generate_winner_meter(home: str, away: str, a: dict) -> str:
    """Broadcast-style winner meter."""
    hw, dr, aw = a["home_win_pct"], a["draw_pct"], a["away_win_pct"]

    def bar(pct: float, width: int = 20) -> str:
        filled = int(round((pct / 100) * width))
        return "¦" * filled + "¦" * (width - filled)

    return "\n".join([
        f"?? WINNER METER | {home} vs {away}",
        f"{home:<18} [{bar(hw)}] {hw:.1f}%",
        f"{'Draw':<18} [{bar(dr)}] {dr:.1f}%",
        f"{away:<18} [{bar(aw)}] {aw:.1f}%",
    ])


def generate_commentator_intro(home: str, away: str, a: dict) -> str:
    """Short network-style opening line."""
    fav = a["favourite"]
    dog = a["underdog"]
    up = a["upset_prob"]

    if fav == home:
        fav_pct = a["home_win_pct"]
    else:
        fav_pct = a["away_win_pct"]

    return (
        f"??? COMMENTATOR INTRO\n\n"
        f"Welcome in to {home} against {away}. "
        f"According to Mundialista AI, {fav} comes in as the favorite at {fav_pct:.1f}%, "
        f"but {dog} still holds an upset chance of {up:.1f}%. "
        f"Expect a match with plenty to watch from the opening whistle."
    )


def generate_lower_third(home: str, away: str, a: dict) -> str:
    """Short lower-third banner text."""
    likely = _format_scoreline_entry(a["top5_scorelines"][0]) if a["top5_scorelines"] else "N/A"
    return (
        f"?? LOWER THIRD\n"
        f"AI PREDICTION: {home} {a['home_win_pct']:.1f}% | "
        f"DRAW {a['draw_pct']:.1f}% | "
        f"{away} {a['away_win_pct']:.1f}%\n"
        f"MOST LIKELY SCORE: {likely}"
    )


def generate_chaos_meter(home: str, away: str, a: dict) -> str:
    """Broadcast-style chaos meter / shock index."""
    up = a["upset_prob"]
    draw = a["draw_pct"]
    rank_gap = abs(a["home_rank"] - a["away_rank"])

    score = 0.0
    score += min(up, 40) * 0.9
    score += min(draw, 35) * 0.5
    score += max(0, 25 - min(rank_gap, 25)) * 1.2
    chaos = min(score, 100.0)

    if chaos >= 75:
        label = "?? CHAOS WATCH"
    elif chaos >= 55:
        label = "?? VOLATILE"
    elif chaos >= 35:
        label = "?? TENSE"
    else:
        label = "?? ROUTINE"

    return (
        f"??? CHAOS METER | {home} vs {away}\n"
        f"{label} — {chaos:.1f}/100\n"
        f"Upset pressure: {up:.1f}% | Draw pressure: {draw:.1f}% | Rank gap: {rank_gap}"
    )


def generate_key_battle(home: str, away: str, a: dict) -> str:
    """Key battle segment for studio shows."""
    xg_edge = a["home_exp"] - a["away_exp"]

    if abs(xg_edge) < 0.15:
        edge_text = "Neither team owns a major expected-goals edge."
    elif xg_edge > 0:
        edge_text = f"{home} carries the attacking edge at +{xg_edge:.2f} xG."
    else:
        edge_text = f"{away} carries the attacking edge at +{abs(xg_edge):.2f} xG."

    return (
        f"?? KEY BATTLE\n"
        f"FIFA Ranking Matchup: #{a['home_rank']} vs #{a['away_rank']}\n"
        f"{edge_text}\n"
        f"Underdog threat level: {a['upset_prob']:.1f}% for {a['underdog']}."
    )


def generate_storylines(home: str, away: str, a: dict) -> str:
    """Top 5 producer-ready storylines."""
    lines = [
        f"?? TOP 5 STORYLINES | {home} vs {away}",
        f"1. {a['favourite']} enters as the AI favorite.",
        f"2. {a['underdog']} still has a live upset chance at {a['upset_prob']:.1f}%.",
        f"3. Expected goals project this matchup at {a['home_exp']:.2f} - {a['away_exp']:.2f}.",
        f"4. The FIFA ranking battle is #{a['home_rank']} vs #{a['away_rank']}.",
    ]

    if a["top5_scorelines"]:
        lines.append(f"5. Most likely scoreline: {_format_scoreline_entry(a['top5_scorelines'][0])}.")
    else:
        lines.append("5. No single scoreline clearly dominates the simulations.")

    return "\n".join(lines)


def generate_star_impact_card(home: str, away: str) -> str:
    """Star impact card."""
    home_resolved = resolve_team_name(home)
    away_resolved = resolve_team_name(away)

    try:
        hs = get_team_star_impact(home_resolved)
    except Exception:
        hs = "N/A"

    try:
        aws = get_team_star_impact(away_resolved)
    except Exception:
        aws = "N/A"

    return (
        f"? STAR IMPACT CARD\n"
        f"{home}: {hs}\n"
        f"{away}: {aws}"
    )


def generate_prediction_verdict(home: str, away: str, a: dict) -> str:
    """Simple headline verdict."""
    winner = _winner_name(home, away, a)
    if winner == "Draw":
        verdict = "Too close to call — the draw is very much alive."
    else:
        verdict = f"The AI leans toward {winner}."

    return (
        f"?? AI VERDICT\n"
        f"{verdict}\n"
        f"Win probabilities: {home} {a['home_win_pct']:.1f}% | "
        f"Draw {a['draw_pct']:.1f}% | {away} {a['away_win_pct']:.1f}%"
    )


def generate_producer_notes(home: str, away: str, a: dict) -> str:
    """Quick producer notes for a studio rundown."""
    likely = _format_scoreline_entry(a["top5_scorelines"][0]) if a["top5_scorelines"] else "N/A"
    return "\n".join([
        f"??? PRODUCER NOTES | {home} vs {away}",
        f"- Favorite: {a['favourite']}",
        f"- Underdog: {a['underdog']}",
        f"- Upset chance: {a['upset_prob']:.1f}%",
        f"- Expected goals: {home} {a['home_exp']:.2f} / {away} {a['away_exp']:.2f}",
        f"- Most likely score: {likely}",
        f"- Match type: {a.get('match_type', 'Competitive')}",
    ])


def generate_headline_pack(home: str, away: str, a: dict) -> str:
    """Headline options for social, studio, or article usage."""
    winner = _winner_name(home, away, a)
    loser = away if winner == home else home

    if winner == "Draw":
        headline1 = f"{home} vs {away}: AI sees a coin-flip clash"
        headline2 = f"No clear favorite as {home} and {away} collide"
        headline3 = f"Tight battle ahead: draw danger high in {home} vs {away}"
    else:
        headline1 = f"{winner} favored in AI forecast against {loser}"
        headline2 = f"{winner} gets the edge in Mundialista AI projection"
        headline3 = f"Can {a['underdog']} flip the script against {winner}?"

    return "\n".join([
        "?? HEADLINE PACK",
        f"1. {headline1}",
        f"2. {headline2}",
        f"3. {headline3}",
    ])


def generate_on_air_tease(home: str, away: str, a: dict) -> str:
    """Short tease line before ad-break or segment intro."""
    likely = _winner_name(home, away, a)
    return (
        f"?? ON-AIR TEASE\n"
        f"Coming up: {home} vs {away}. "
        f"Will {likely} justify the AI projection, "
        f"or can {a['underdog']} deliver the surprise?"
    )


def generate_match_card(home: str, away: str, a: dict) -> str:
    """Compact all-in-one TV card."""
    likely = _format_scoreline_entry(a["top5_scorelines"][0]) if a["top5_scorelines"] else "N/A"
    return "\n".join([
        f"?? MATCH CARD | {home} vs {away}",
        f"Rankings: #{a['home_rank']} vs #{a['away_rank']}",
        f"Win %: {home} {a['home_win_pct']:.1f} | Draw {a['draw_pct']:.1f} | {away} {a['away_win_pct']:.1f}",
        f"xG: {a['home_exp']:.2f} - {a['away_exp']:.2f}",
        f"Top score: {likely}",
        f"Upset watch: {a['upset_prob']:.1f}% for {a['underdog']}",
    ])


def generate_three_keys(home: str, away: str, a: dict) -> str:
    """Three keys to the match."""
    keys = []

    if a["home_exp"] > a["away_exp"]:
        keys.append(f"1. {home} must turn its xG edge into early pressure.")
    elif a["away_exp"] > a["home_exp"]:
        keys.append(f"1. {away} must turn its xG edge into clean finishing.")
    else:
        keys.append("1. Finishing efficiency could decide an otherwise even match.")

    if a["draw_pct"] >= 25:
        keys.append("2. A slow, tense game state increases the draw threat.")
    else:
        keys.append("2. An early goal may completely reshape the tactical flow.")

    if a["upset_prob"] >= 30:
        keys.append(f"3. {a['underdog']} is live — this is a dangerous upset spot.")
    else:
        keys.append(f"3. {a['favourite']} should control the match if it avoids mistakes.")

    return "?? THREE KEYS TO THE MATCH\n" + "\n".join(keys)


def generate_upset_scale(home: str, away: str, a: dict) -> str:
    """Visual upset scale."""
    up = a["upset_prob"]

    if up >= 40:
        label = "?? RED ALERT"
    elif up >= 30:
        label = "?? HIGH ALERT"
    elif up >= 20:
        label = "?? WATCHABLE"
    else:
        label = "? STABLE"

    width = 20
    filled = int(round((up / 100) * width))
    bar = "¦" * filled + "¦" * (width - filled)

    return (
        f"?? UPSET SCALE\n"
        f"{a['underdog']} vs {a['favourite']}\n"
        f"[{bar}] {up:.1f}%\n"
        f"Status: {label}"
    )


def generate_scoreline_panel(home: str, away: str, a: dict) -> str:
    """Top scoreline panel."""
    lines = [f"?? SCORELINE PANEL | {home} vs {away}"]
    if not a["top5_scorelines"]:
        lines.append("No scoreline data available.")
        return "\n".join(lines)

    for i, sc in enumerate(a["top5_scorelines"][:5], 1):
        lines.append(f"{i}. {_format_scoreline_entry(sc)}")

    return "\n".join(lines)


def generate_full_broadcast_pack(home: str, away: str, a: dict) -> str:
    """All-in-one broadcast bundle."""
    sections = [
        generate_match_card(home, away, a),
        generate_winner_meter(home, away, a),
        generate_commentator_intro(home, away, a),
        generate_lower_third(home, away, a),
        generate_chaos_meter(home, away, a),
        generate_key_battle(home, away, a),
        generate_three_keys(home, away, a),
        generate_scoreline_panel(home, away, a),
    ]
    return "\n\n".join(sections)
