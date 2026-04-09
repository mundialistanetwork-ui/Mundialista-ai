def _format_scoreline_entry(sc):
    if not isinstance(sc, (list, tuple)) or len(sc) < 2:
        return "N/A"
    raw_score, pct = sc[0], sc[1]
    if isinstance(raw_score, (list, tuple)) and len(raw_score) == 2:
        score_str = str(raw_score[0]) + "-" + str(raw_score[1])
    else:
        score_str = str(raw_score)
    if isinstance(pct, (int, float)):
        if pct < 1:
            pct = pct * 100
        return score_str + " (" + str(round(pct, 1)) + "%)"
    return score_str


def _winner_name(home, away, a):
    hw = a["home_win_pct"]
    dr = a["draw_pct"]
    aw = a["away_win_pct"]
    if hw >= dr and hw >= aw:
        return home
    elif aw >= hw and aw >= dr:
        return away
    return "Draw"


def generate_winner_meter(home, away, a):
    hw = a["home_win_pct"]
    dr = a["draw_pct"]
    aw = a["away_win_pct"]
    def bar(pct, width=20):
        filled = int(round((pct / 100.0) * width))
        return "#" * filled + "." * (width - filled)
    lines = []
    lines.append("WINNER METER | " + home + " vs " + away)
    lines.append(home.ljust(18) + " [" + bar(hw) + "] " + str(round(hw, 1)) + "%")
    lines.append("Draw".ljust(18) + " [" + bar(dr) + "] " + str(round(dr, 1)) + "%")
    lines.append(away.ljust(18) + " [" + bar(aw) + "] " + str(round(aw, 1)) + "%")
    return "\n".join(lines)


def generate_commentator_intro(home, away, a):
    fav = a["favourite"]
    dog = a["underdog"]
    up = a["upset_prob"]
    if fav == home:
        fav_pct = a["home_win_pct"]
    else:
        fav_pct = a["away_win_pct"]
    text = "COMMENTATOR INTRO\n\n"
    text += "Welcome in to " + home + " against " + away + ". "
    text += "According to Mundialista AI, " + fav + " comes in as the favorite at " + str(round(fav_pct, 1)) + "%, "
    text += "but " + dog + " still holds an upset chance of " + str(round(up, 1)) + "%. "
    text += "Expect a match with plenty to watch from the opening whistle."
    return text


def generate_lower_third(home, away, a):
    if a["top5_scorelines"]:
        likely = _format_scoreline_entry(a["top5_scorelines"][0])
    else:
        likely = "N/A"
    text = "LOWER THIRD\n"
    text += "AI PREDICTION: " + home + " " + str(round(a["home_win_pct"], 1)) + "% | "
    text += "DRAW " + str(round(a["draw_pct"], 1)) + "% | "
    text += away + " " + str(round(a["away_win_pct"], 1)) + "%\n"
    text += "MOST LIKELY SCORE: " + likely
    return text


def generate_chaos_meter(home, away, a):
    up = a["upset_prob"]
    draw = a["draw_pct"]
    rank_gap = abs(a["home_rank"] - a["away_rank"])
    score = min(up, 40) * 0.9 + min(draw, 35) * 0.5 + max(0, 25 - min(rank_gap, 25)) * 1.2
    chaos = min(score, 100.0)
    if chaos >= 75:
        label = "CHAOS WATCH"
    elif chaos >= 55:
        label = "VOLATILE"
    elif chaos >= 35:
        label = "TENSE"
    else:
        label = "ROUTINE"
    text = "CHAOS METER | " + home + " vs " + away + "\n"
    text += label + " - " + str(round(chaos, 1)) + "/100\n"
    text += "Upset: " + str(round(up, 1)) + "% | Draw: " + str(round(draw, 1)) + "% | Gap: " + str(rank_gap)
    return text


def generate_key_battle(home, away, a):
    xg_edge = a["home_exp"] - a["away_exp"]
    if abs(xg_edge) < 0.15:
        edge = "Neither team owns a major xG edge."
    elif xg_edge > 0:
        edge = home + " carries the attacking edge at +" + str(round(xg_edge, 2)) + " xG."
    else:
        edge = away + " carries the attacking edge at +" + str(round(abs(xg_edge), 2)) + " xG."
    text = "KEY BATTLE\n"
    text += "Rankings: #" + str(a["home_rank"]) + " vs #" + str(a["away_rank"]) + "\n"
    text += edge + "\n"
    text += "Upset threat: " + str(round(a["upset_prob"], 1)) + "% for " + a["underdog"] + "."
    return text


def generate_storylines(home, away, a):
    lines = []
    lines.append("TOP 5 STORYLINES | " + home + " vs " + away)
    lines.append("1. " + a["favourite"] + " enters as the AI favorite.")
    lines.append("2. " + a["underdog"] + " has a live upset chance at " + str(round(a["upset_prob"], 1)) + "%.")
    lines.append("3. Expected goals: " + str(round(a["home_exp"], 2)) + " - " + str(round(a["away_exp"], 2)) + ".")
    lines.append("4. Rankings: #" + str(a["home_rank"]) + " vs #" + str(a["away_rank"]) + ".")
    if a["top5_scorelines"]:
        lines.append("5. Most likely: " + _format_scoreline_entry(a["top5_scorelines"][0]) + ".")
    else:
        lines.append("5. No dominant scoreline.")
    return "\n".join(lines)


def generate_star_impact_card(home, away, resolve_team_name, get_team_star_impact):
    home_r = resolve_team_name(home)
    away_r = resolve_team_name(away)
    try:
        hs = str(get_team_star_impact(home_r))
    except Exception:
        hs = "N/A"
    try:
        aws = str(get_team_star_impact(away_r))
    except Exception:
        aws = "N/A"
    return "STAR IMPACT CARD\n" + home + ": " + hs + "\n" + away + ": " + aws


def generate_prediction_verdict(home, away, a):
    winner = _winner_name(home, away, a)
    if winner == "Draw":
        verdict = "Too close to call; the draw is alive."
    else:
        verdict = "The AI leans toward " + winner + "."
    text = "AI VERDICT\n" + verdict + "\n"
    text += home + " " + str(round(a["home_win_pct"], 1)) + "% | "
    text += "Draw " + str(round(a["draw_pct"], 1)) + "% | "
    text += away + " " + str(round(a["away_win_pct"], 1)) + "%"
    return text


def generate_producer_notes(home, away, a):
    if a["top5_scorelines"]:
        likely = _format_scoreline_entry(a["top5_scorelines"][0])
    else:
        likely = "N/A"
    lines = []
    lines.append("PRODUCER NOTES | " + home + " vs " + away)
    lines.append("- Favorite: " + a["favourite"])
    lines.append("- Underdog: " + a["underdog"])
    lines.append("- Upset: " + str(round(a["upset_prob"], 1)) + "%")
    lines.append("- xG: " + home + " " + str(round(a["home_exp"], 2)) + " / " + away + " " + str(round(a["away_exp"], 2)))
    lines.append("- Top score: " + likely)
    lines.append("- Match type: " + a.get("match_type", "Competitive"))
    return "\n".join(lines)


def generate_headline_pack(home, away, a):
    winner = _winner_name(home, away, a)
    loser = away if winner == home else home
    if winner == "Draw":
        h1 = home + " vs " + away + ": AI sees a coin-flip"
        h2 = "No clear favorite as " + home + " and " + away + " collide"
        h3 = "Draw danger high in " + home + " vs " + away
    else:
        h1 = winner + " favored against " + loser
        h2 = winner + " gets AI edge in projection"
        h3 = "Can " + a["underdog"] + " flip the script against " + winner + "?"
    return "\n".join(["HEADLINE PACK", "1. " + h1, "2. " + h2, "3. " + h3])


def generate_on_air_tease(home, away, a):
    likely = _winner_name(home, away, a)
    text = "ON-AIR TEASE\n"
    text += "Coming up: " + home + " vs " + away + ". "
    text += "Will " + likely + " justify the AI projection, "
    text += "or can " + a["underdog"] + " deliver the surprise?"
    return text


def generate_match_card(home, away, a):
    if a["top5_scorelines"]:
        likely = _format_scoreline_entry(a["top5_scorelines"][0])
    else:
        likely = "N/A"
    lines = []
    lines.append("MATCH CARD | " + home + " vs " + away)
    lines.append("Rankings: #" + str(a["home_rank"]) + " vs #" + str(a["away_rank"]))
    lines.append("Win: " + home + " " + str(round(a["home_win_pct"], 1)) + " | Draw " + str(round(a["draw_pct"], 1)) + " | " + away + " " + str(round(a["away_win_pct"], 1)))
    lines.append("xG: " + str(round(a["home_exp"], 2)) + " - " + str(round(a["away_exp"], 2)))
    lines.append("Top score: " + likely)
    lines.append("Upset: " + str(round(a["upset_prob"], 1)) + "% for " + a["underdog"])
    return "\n".join(lines)


def generate_three_keys(home, away, a):
    keys = []
    if a["home_exp"] > a["away_exp"]:
        keys.append("1. " + home + " must convert its xG edge early.")
    elif a["away_exp"] > a["home_exp"]:
        keys.append("1. " + away + " must convert its xG edge.")
    else:
        keys.append("1. Finishing efficiency decides this even match.")
    if a["draw_pct"] >= 25:
        keys.append("2. Slow pace increases draw threat.")
    else:
        keys.append("2. An early goal reshapes the tactical flow.")
    if a["upset_prob"] >= 30:
        keys.append("3. " + a["underdog"] + " is live - dangerous upset spot.")
    else:
        keys.append("3. " + a["favourite"] + " should control if it avoids mistakes.")
    return "THREE KEYS\n" + "\n".join(keys)


def generate_upset_scale(home, away, a):
    up = a["upset_prob"]
    if up >= 40:
        label = "RED ALERT"
    elif up >= 30:
        label = "HIGH ALERT"
    elif up >= 20:
        label = "WATCHABLE"
    else:
        label = "STABLE"
    filled = int(round((up / 100.0) * 20))
    bar = "#" * filled + "." * (20 - filled)
    text = "UPSET SCALE\n"
    text += a["underdog"] + " vs " + a["favourite"] + "\n"
    text += "[" + bar + "] " + str(round(up, 1)) + "%\n"
    text += "Status: " + label
    return text


def generate_scoreline_panel(home, away, a):
    lines = ["SCORELINE PANEL | " + home + " vs " + away]
    if not a["top5_scorelines"]:
        lines.append("No data.")
        return "\n".join(lines)
    for i, sc in enumerate(a["top5_scorelines"][:5], 1):
        lines.append(str(i) + ". " + _format_scoreline_entry(sc))
    return "\n".join(lines)


def generate_full_broadcast_pack(home, away, a):
    parts = [
        generate_match_card(home, away, a),
        "",
        generate_winner_meter(home, away, a),
        "",
        generate_commentator_intro(home, away, a),
        "",
        generate_lower_third(home, away, a),
        "",
        generate_chaos_meter(home, away, a),
        "",
        generate_key_battle(home, away, a),
        "",
        generate_three_keys(home, away, a),
        "",
        generate_scoreline_panel(home, away, a),
    ]
    return "\n".join(parts)
