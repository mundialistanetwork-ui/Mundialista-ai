import numpy as np
import pandas as pd
from scipy.stats import poisson
import math
import unicodedata
from datetime import datetime, timedelta

CONFIG = {
    "GLOBAL_GF": 1.36,
    "GLOBAL_GA": 1.36,
    "SHRINK_K": 8,
    "LAST_N_MATCHES": 20,
    "DECAY_RATE": 0.003,
    "HOME_ADVANTAGE": 1.06,
    "AWAY_DISADVANTAGE": 0.94,
    "RANK_WEIGHT_TOP": 0.30,
    "RANK_WEIGHT_OTHER": 0.20,
    "TOP_TEAM_THRESHOLD": 30,
    "MAX_RATIO": 1.40,
    "DIXON_COLES_RHO": -0.08,
    "MAX_GOALS": 8,
    "N_SIMULATIONS": 10200,
    "TOURNAMENT_WEIGHTS": {
        "FIFA World Cup": 1.0,
        "Copa America": 0.9,
        "UEFA Euro": 0.9,
        "Africa Cup of Nations": 0.85,
        "AFC Asian Cup": 0.85,
        "CONCACAF Gold Cup": 0.8,
        "UEFA Nations League": 0.85,
        "FIFA World Cup qualification": 0.8,
        "Friendly": 0.5,
    },
    "DEFAULT_TOURNAMENT_WEIGHT": 0.65,
    "H2H_MATCHES": 8,
    "H2H_WEIGHT": 0.05,
    "STAR_MIN_GOALS": 4,
    "STAR_RECENT_DAYS": 900,
}

STAR_PLAYERS = {
    "Argentina": {
        "Lionel Messi": {"attack": 1.15, "status": "active"},
        "Lautaro Martinez": {"attack": 1.08, "status": "active"},
        "Julian Alvarez": {"attack": 1.06, "status": "active"},
    },
    "France": {
        "Kylian Mbappe": {"attack": 1.15, "status": "active"},
        "Antoine Griezmann": {"attack": 1.06, "status": "active"},
    },
    "Brazil": {
        "Vinicius Jr": {"attack": 1.12, "status": "active"},
        "Raphinha": {"attack": 1.06, "status": "active"},
        "Rodrygo": {"attack": 1.05, "status": "active"},
    },
    "England": {
        "Harry Kane": {"attack": 1.12, "status": "active"},
        "Bukayo Saka": {"attack": 1.08, "status": "active"},
        "Jude Bellingham": {"attack": 1.10, "status": "active"},
    },
    "Spain": {
        "Lamine Yamal": {"attack": 1.10, "status": "active"},
        "Alvaro Morata": {"attack": 1.06, "status": "active"},
        "Dani Olmo": {"attack": 1.06, "status": "active"},
    },
    "Germany": {
        "Florian Wirtz": {"attack": 1.10, "status": "active"},
        "Jamal Musiala": {"attack": 1.10, "status": "active"},
        "Kai Havertz": {"attack": 1.06, "status": "active"},
    },
    "Portugal": {
        "Cristiano Ronaldo": {"attack": 1.10, "status": "active"},
        "Bruno Fernandes": {"attack": 1.08, "status": "active"},
        "Bernardo Silva": {"attack": 1.06, "status": "active"},
    },
    "Norway": {
        "Erling Haaland": {"attack": 1.18, "status": "active"},
        "Martin Odegaard": {"attack": 1.08, "status": "active"},
    },
    "Egypt": {
        "Mohamed Salah": {"attack": 1.12, "status": "active"},
    },
    "South Korea": {
        "Son Heung-min": {"attack": 1.12, "status": "active"},
    },
    "Belgium": {
        "Romelu Lukaku": {"attack": 1.10, "status": "active"},
        "Kevin De Bruyne": {"attack": 1.10, "status": "active"},
    },
    "Netherlands": {
        "Cody Gakpo": {"attack": 1.08, "status": "active"},
        "Memphis Depay": {"attack": 1.06, "status": "active"},
    },
    "Colombia": {
        "Luis Diaz": {"attack": 1.08, "status": "active"},
        "James Rodriguez": {"attack": 1.06, "status": "active"},
    },
    "Uruguay": {
        "Darwin Nunez": {"attack": 1.08, "status": "active"},
        "Federico Valverde": {"attack": 1.06, "status": "active"},
    },
    "Croatia": {
        "Luka Modric": {"attack": 1.06, "status": "active"},
    },
    "Japan": {
        "Takefusa Kubo": {"attack": 1.06, "status": "active"},
        "Kaoru Mitoma": {"attack": 1.06, "status": "active"},
    },
    "United States": {
        "Christian Pulisic": {"attack": 1.08, "status": "active"},
        "Weston McKennie": {"attack": 1.04, "status": "active"},
    },
    "Mexico": {
        "Raul Jimenez": {"attack": 1.06, "status": "active"},
    },
    "Senegal": {
        "Sadio Mane": {"attack": 1.10, "status": "active"},
    },
    "Morocco": {
        "Hakim Ziyech": {"attack": 1.07, "status": "active"},
        "Achraf Hakimi": {"attack": 1.05, "status": "active"},
    },
    "Italy": {
        "Federico Chiesa": {"attack": 1.06, "status": "active"},
    },
}

_results_cache = None
_rankings_cache = None


def load_results():
    global _results_cache
    if _results_cache is not None:
        return _results_cache
    try:
        df = pd.read_csv("data/results.csv")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        _results_cache = df
        return df
    except FileNotFoundError:
        return pd.DataFrame()


def load_rankings():
    global _rankings_cache
    if _rankings_cache is not None:
        return _rankings_cache
    try:
        df = pd.read_csv("data/rankings.csv")
        _rankings_cache = df
        return df
    except FileNotFoundError:
        return pd.DataFrame()




_goalscorers_cache = None


def load_goalscorers():
    global _goalscorers_cache
    if _goalscorers_cache is not None:
        return _goalscorers_cache
    try:
        df = pd.read_csv("data/goalscorers.csv")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        _goalscorers_cache = df
        return df
    except FileNotFoundError:
        return pd.DataFrame()

def get_all_teams():
    df = load_results()
    if df.empty:
        return []
    teams = set(df["home_team"].unique()) | set(df["away_team"].unique())
    return sorted(teams)


def get_team_ranking(team):
    rankings = load_rankings()
    if rankings.empty:
        return 100
    row = rankings[rankings["country_full"] == team]
    if len(row) > 0:
        return int(row.iloc[0]["rank"])
    return 100


def get_team_points(team):
    rankings = load_rankings()
    if rankings.empty:
        return 1000
    row = rankings[rankings["country_full"] == team]
    if len(row) > 0:
        return int(row.iloc[0]["total_points"])
    return 1000




def normalize_name(name):
    if not isinstance(name, str):
        return str(name)
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = nfkd.encode("ascii", "ignore").decode("ascii")
    return ascii_name.strip()



def names_match(name1, name2):
    n1 = normalize_name(name1).lower().strip()
    n2 = normalize_name(name2).lower().strip()
    if n1 == n2:
        return True
    for suffix in [' jr', ' junior', ' sr', ' senior', ' ii', ' iii']:
        n1 = n1.replace(suffix, '').strip()
        n2 = n2.replace(suffix, '').strip()
    if n1 == n2:
        return True
    if len(n1) > 3 and len(n2) > 3:
        if n1 in n2 or n2 in n1:
            return True
    return False


def derive_star_players(team):
    gs = load_goalscorers()
    if gs.empty:
        return {}
    cutoff = datetime.now() - timedelta(days=CONFIG["STAR_RECENT_DAYS"])
    recent = gs[gs["date"] >= cutoff].copy()
    if recent.empty:
        return {}
    team_goals = recent[recent["team"] == team].copy()
    if "own_goal" in team_goals.columns:
        team_goals = team_goals[team_goals["own_goal"] != True]
    if team_goals.empty:
        return {}
    if "scorer" not in team_goals.columns:
        return {}
    player_goals = team_goals.groupby("scorer").agg(
        total_goals=("scorer", "count"),
        matches=("date", "nunique")
    ).reset_index()
    player_goals = player_goals[player_goals["total_goals"] >= CONFIG["STAR_MIN_GOALS"]]
    if player_goals.empty:
        return {}
    player_goals["gpm"] = player_goals["total_goals"] / player_goals["matches"]
    player_goals = player_goals[player_goals["gpm"] >= 0.20]
    if player_goals.empty:
        return {}
    team_matches = recent[(recent["home_team"] == team) | (recent["away_team"] == team)]
    team_match_count = team_matches["date"].nunique()
    if team_match_count < 1:
        team_match_count = 1
    team_total_goals = len(team_goals)
    team_avg_gpm = team_total_goals / team_match_count if team_match_count > 0 else 1.0
    result = {}
    for _, row in player_goals.iterrows():
        name = row["scorer"]
        gpm = row["gpm"]
        if team_avg_gpm > 0:
            relative = gpm / team_avg_gpm
        else:
            relative = 1.0
        boost = 1.0 + min(0.18, gpm * 0.08 + (relative - 1.0) * 0.04)
        boost = max(1.02, min(boost, 1.20))
        norm = normalize_name(name)
        result[norm] = {"attack": round(boost, 3), "status": "active", "source": "data"}
    return result


def get_team_star_impact(team):
    manual = STAR_PLAYERS.get(team, {})
    derived = derive_star_players(team)
    merged = {}
    for name, data in manual.items():
        if data.get("status") == "active":
            norm = normalize_name(name)
            merged[norm] = data.copy()
    for name, data in derived.items():
        matched_key = None
        for existing_name in merged:
            if names_match(name, existing_name):
                matched_key = existing_name
                break
        if matched_key:
            old_boost = merged[matched_key].get("attack", 1.0)
            new_boost = data.get("attack", 1.0)
            merged[matched_key]["attack"] = round(max(old_boost, new_boost), 3)
        else:
            merged[name] = data
    if not merged:
        return {"attack": 1.0, "players": []}
    sorted_players = sorted(merged.values(), key=lambda x: x.get("attack", 1.0), reverse=True)
    total_boost = 1.0
    for i, data in enumerate(sorted_players):
        individual = data.get("attack", 1.0) - 1.0
        diminish = 0.55 / (1.0 + 0.3 * i)
        total_boost += individual * diminish
    total_boost = min(total_boost, 1.25)
    return {"attack": round(total_boost, 3), "players": list(merged.keys())}


def get_ranking_factor(rank):
    return 1.0 + 0.10 * math.log(201.0 / max(rank, 1))


def shrink_to_global(value, n_matches, global_mean):
    k = CONFIG["SHRINK_K"]
    return (n_matches * value + k * global_mean) / (n_matches + k)


def get_tournament_weight(tournament_name):
    if not tournament_name or not isinstance(tournament_name, str):
        return CONFIG["DEFAULT_TOURNAMENT_WEIGHT"]
    weights = CONFIG["TOURNAMENT_WEIGHTS"]
    for key, val in weights.items():
        if key.lower() in tournament_name.lower():
            return val
    return CONFIG["DEFAULT_TOURNAMENT_WEIGHT"]


def get_time_weight(match_date):
    decay_rate = CONFIG["DECAY_RATE"]
    if not isinstance(match_date, (pd.Timestamp, datetime)):
        return 0.5
    days_ago = (datetime.now() - pd.Timestamp(match_date).to_pydatetime()).days
    if days_ago < 0:
        days_ago = 0
    return math.exp(-decay_rate * days_ago)


def get_opponent_strength(opponent_rank):
    return get_ranking_factor(opponent_rank) / get_ranking_factor(50)


def get_team_stats(team):
    df = load_results()
    last_n = CONFIG["LAST_N_MATCHES"]
    default = {
        "attack": 1.0,
        "defense": 1.0,
        "avg_gf": CONFIG["GLOBAL_GF"],
        "avg_ga": CONFIG["GLOBAL_GA"],
        "home_gf": CONFIG["GLOBAL_GF"],
        "away_gf": CONFIG["GLOBAL_GF"],
        "matches": 0,
        "weighted_gf": CONFIG["GLOBAL_GF"],
        "weighted_ga": CONFIG["GLOBAL_GA"],
    }
    if df.empty:
        return default
    home_df = df[df["home_team"] == team].copy()
    away_df = df[df["away_team"] == team].copy()
    if home_df.empty and away_df.empty:
        return default
    home_df = home_df.tail(last_n)
    away_df = away_df.tail(last_n)
    rows = []
    for _, r in home_df.iterrows():
        opp = r.get("away_team", "")
        opp_rank = get_team_ranking(opp)
        tw = get_time_weight(r.get("date"))
        tourney = get_tournament_weight(r.get("tournament", ""))
        opp_str = get_opponent_strength(opp_rank)
        w = tw * tourney * opp_str
        rows.append({"gf": r.get("home_score", 0), "ga": r.get("away_score", 0), "weight": w})
    for _, r in away_df.iterrows():
        opp = r.get("home_team", "")
        opp_rank = get_team_ranking(opp)
        tw = get_time_weight(r.get("date"))
        tourney = get_tournament_weight(r.get("tournament", ""))
        opp_str = get_opponent_strength(opp_rank)
        w = tw * tourney * opp_str
        rows.append({"gf": r.get("away_score", 0), "ga": r.get("home_score", 0), "weight": w})
    if not rows:
        return default
    total_w = sum(r["weight"] for r in rows)
    if total_w < 0.001:
        total_w = 1.0
    weighted_gf = sum(r["gf"] * r["weight"] for r in rows) / total_w
    weighted_ga = sum(r["ga"] * r["weight"] for r in rows) / total_w
    n = len(rows)
    gf_shrunk = shrink_to_global(weighted_gf, n, CONFIG["GLOBAL_GF"])
    ga_shrunk = shrink_to_global(weighted_ga, n, CONFIG["GLOBAL_GA"])
    attack = gf_shrunk / CONFIG["GLOBAL_GF"] if CONFIG["GLOBAL_GF"] > 0 else 1.0
    defense = ga_shrunk / CONFIG["GLOBAL_GA"] if CONFIG["GLOBAL_GA"] > 0 else 1.0
    simple_gf = sum(r["gf"] for r in rows) / n
    simple_ga = sum(r["ga"] for r in rows) / n
    home_gf_val = home_df["home_score"].mean() if not home_df.empty else CONFIG["GLOBAL_GF"]
    away_gf_val = away_df["away_score"].mean() if not away_df.empty else CONFIG["GLOBAL_GF"]
    return {
        "attack": attack,
        "defense": defense,
        "avg_gf": simple_gf,
        "avg_ga": simple_ga,
        "home_gf": home_gf_val,
        "away_gf": away_gf_val,
        "matches": n,
        "weighted_gf": weighted_gf,
        "weighted_ga": weighted_ga,
    }


def dixon_coles_adjust(prob, goals_a, goals_b, lambda_a, lambda_b, rho):
    if goals_a == 0 and goals_b == 0:
        return prob * (1.0 + rho * lambda_a * lambda_b)
    elif goals_a == 0 and goals_b == 1:
        return prob * (1.0 - rho * lambda_a)
    elif goals_a == 1 and goals_b == 0:
        return prob * (1.0 - rho * lambda_b)
    elif goals_a == 1 and goals_b == 1:
        return prob * (1.0 + rho)
    else:
        return prob


def get_score_matrix(lambda_a, lambda_b, max_goals=None):
    if max_goals is None:
        max_goals = CONFIG["MAX_GOALS"]
    rho = CONFIG["DIXON_COLES_RHO"]
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            base = poisson.pmf(i, lambda_a) * poisson.pmf(j, lambda_b)
            matrix[i, j] = dixon_coles_adjust(base, i, j, lambda_a, lambda_b, rho)
    total = matrix.sum()
    if total > 0:
        matrix = matrix / total
    return matrix



def get_head_to_head(team_a, team_b):
    df = load_results()
    if df.empty:
        return {"factor_a": 1.0, "factor_b": 1.0, "matches": 0, "wins_a": 0, "wins_b": 0, "draws": 0}
    h2h_n = CONFIG["H2H_MATCHES"]
    mask_ab = (df["home_team"] == team_a) & (df["away_team"] == team_b)
    mask_ba = (df["home_team"] == team_b) & (df["away_team"] == team_a)
    matches = df[mask_ab | mask_ba].copy()
    if matches.empty:
        return {"factor_a": 1.0, "factor_b": 1.0, "matches": 0, "wins_a": 0, "wins_b": 0, "draws": 0}
    if "date" in matches.columns:
        matches = matches.sort_values("date")
    matches = matches.tail(h2h_n)
    wins_a = 0
    wins_b = 0
    draws = 0
    goals_a = 0
    goals_b = 0
    for _, r in matches.iterrows():
        if r["home_team"] == team_a:
            ga = r.get("home_score", 0)
            gb = r.get("away_score", 0)
        else:
            ga = r.get("away_score", 0)
            gb = r.get("home_score", 0)
        goals_a += ga
        goals_b += gb
        if ga > gb:
            wins_a += 1
        elif gb > ga:
            wins_b += 1
        else:
            draws += 1
    n = len(matches)
    if n == 0:
        return {"factor_a": 1.0, "factor_b": 1.0, "matches": 0, "wins_a": 0, "wins_b": 0, "draws": 0}
    win_rate_a = wins_a / n
    win_rate_b = wins_b / n
    h2h_w = CONFIG["H2H_WEIGHT"]
    factor_a = 1.0 + h2h_w * (win_rate_a - win_rate_b)
    factor_b = 1.0 + h2h_w * (win_rate_b - win_rate_a)
    return {
        "factor_a": round(factor_a, 4),
        "factor_b": round(factor_b, 4),
        "matches": n,
        "wins_a": wins_a,
        "wins_b": wins_b,
        "draws": draws,
        "goals_a": goals_a,
        "goals_b": goals_b,
    }


def predict(team_a, team_b, home=None):
    stats_a = get_team_stats(team_a)
    stats_b = get_team_stats(team_b)
    rank_a = get_team_ranking(team_a)
    rank_b = get_team_ranking(team_b)
    points_a = get_team_points(team_a)
    points_b = get_team_points(team_b)
    rank_factor_a = get_ranking_factor(rank_a)
    rank_factor_b = get_ranking_factor(rank_b)
    both_top = rank_a <= CONFIG["TOP_TEAM_THRESHOLD"] and rank_b <= CONFIG["TOP_TEAM_THRESHOLD"]
    attack_a = stats_a["attack"]
    defense_a = stats_a["defense"]
    attack_b = stats_b["attack"]
    defense_b = stats_b["defense"]
    lambda_form_a = attack_a * defense_b * CONFIG["GLOBAL_GF"]
    lambda_form_b = attack_b * defense_a * CONFIG["GLOBAL_GF"]
    lambda_rank_a = CONFIG["GLOBAL_GF"] * rank_factor_a / rank_factor_b
    lambda_rank_b = CONFIG["GLOBAL_GF"] * rank_factor_b / rank_factor_a
    if both_top:
        rw = CONFIG["RANK_WEIGHT_TOP"]
    else:
        rw = CONFIG["RANK_WEIGHT_OTHER"]
    fw = 1.0 - rw
    lambda_a = rw * lambda_rank_a + fw * lambda_form_a
    lambda_b = rw * lambda_rank_b + fw * lambda_form_b
    star_data_a = get_team_star_impact(team_a)
    star_data_b = get_team_star_impact(team_b)
    star_a = star_data_a["attack"]
    star_b = star_data_b["attack"]
    avg_star = (star_a + star_b) / 2
    relative_star_a = star_a / avg_star if avg_star > 0 else 1.0
    relative_star_b = star_b / avg_star if avg_star > 0 else 1.0
    lambda_a = lambda_a * relative_star_a
    lambda_b = lambda_b * relative_star_b

    # Head-to-head adjustment
    h2h = get_head_to_head(team_a, team_b)
    lambda_a = lambda_a * h2h["factor_a"]
    lambda_b = lambda_b * h2h["factor_b"]

    is_home_a = home == team_a
    is_home_b = home == team_b
    if is_home_a:
        lambda_a = lambda_a * CONFIG["HOME_ADVANTAGE"]
        lambda_b = lambda_b * CONFIG["AWAY_DISADVANTAGE"]
    elif is_home_b:
        lambda_b = lambda_b * CONFIG["HOME_ADVANTAGE"]
        lambda_a = lambda_a * CONFIG["AWAY_DISADVANTAGE"]
    if both_top:
        ratio = lambda_a / lambda_b if lambda_b > 0 else 1.0
        if ratio > CONFIG["MAX_RATIO"]:
            lambda_a = lambda_b * CONFIG["MAX_RATIO"]
        elif ratio < 1.0 / CONFIG["MAX_RATIO"]:
            lambda_b = lambda_a * CONFIG["MAX_RATIO"]
    lambda_a = max(lambda_a, 0.25)
    lambda_b = max(lambda_b, 0.25)
    max_goals = CONFIG["MAX_GOALS"]
    matrix = get_score_matrix(lambda_a, lambda_b, max_goals)
    win_a = 0.0
    draw = 0.0
    win_b = 0.0
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            if i > j:
                win_a += matrix[i, j]
            elif i == j:
                draw += matrix[i, j]
            else:
                win_b += matrix[i, j]
    score_probs = {}
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            score_probs[str(i) + "-" + str(j)] = matrix[i, j]
    top_scores = sorted(score_probs.items(), key=lambda x: -x[1])[:10]
    top_scores = [(s, round(p * CONFIG["N_SIMULATIONS"])) for s, p in top_scores]
    rank_gap = abs(rank_a - rank_b)
    if both_top and rank_gap < 20:
        match_type = "Elite Clash"
    elif rank_gap > 100:
        match_type = "Total Mismatch"
    elif rank_gap > 50:
        match_type = "Clear Favorite"
    else:
        match_type = "Competitive Match"
    n_sims = CONFIG["N_SIMULATIONS"]
    goals_a_sim = np.random.poisson(lambda_a, n_sims)
    goals_b_sim = np.random.poisson(lambda_b, n_sims)
    return {
        "team_a": team_a,
        "team_b": team_b,
        "team_a_win": round(100 * win_a, 1),
        "draw": round(100 * draw, 1),
        "team_b_win": round(100 * win_b, 1),
        "team_a_lambda": round(lambda_a, 3),
        "team_b_lambda": round(lambda_b, 3),
        "team_a_rank": rank_a,
        "team_b_rank": rank_b,
        "team_a_points": points_a,
        "team_b_points": points_b,
        "team_a_stars": star_data_a["players"],
        "team_b_stars": star_data_b["players"],
        "team_a_star_boost": star_a,
        "team_b_star_boost": star_b,
        "team_a_attack": round(stats_a["attack"], 3),
        "team_a_defense": round(stats_a["defense"], 3),
        "team_b_attack": round(stats_b["attack"], 3),
        "team_b_defense": round(stats_b["defense"], 3),
        "match_type": match_type,
        "rank_gap": rank_gap,
        "home": home,
        "h2h_matches": h2h["matches"],
        "h2h_wins_a": h2h.get("wins_a", 0),
        "h2h_wins_b": h2h.get("wins_b", 0),
        "h2h_draws": h2h.get("draws", 0),
        "top_scores": top_scores,
        "goals_a": goals_a_sim,
        "goals_b": goals_b_sim,
        "n_simulations": n_sims,
    }


if __name__ == "__main__":
    print("Testing prediction engine v6...")
    result = predict("Argentina", "Brazil")
    print()
    print(result["team_a"] + " vs " + result["team_b"])
    print("Ranks: #" + str(result["team_a_rank"]) + " vs #" + str(result["team_b_rank"]))
    print("Result: " + str(result["team_a_win"]) + "% | " + str(result["draw"]) + "% | " + str(result["team_b_win"]) + "%")
    print("Lambdas: " + str(result["team_a_lambda"]) + " vs " + str(result["team_b_lambda"]))
    print("Attack/Defense A: " + str(result["team_a_attack"]) + " / " + str(result["team_a_defense"]))
    print("Attack/Defense B: " + str(result["team_b_attack"]) + " / " + str(result["team_b_defense"]))
    print()
    print("Top scores:")
    for item in result["top_scores"][:5]:
        print("  " + str(item[0]) + "  " + str(item[1]))
