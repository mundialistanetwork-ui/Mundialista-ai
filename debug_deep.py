import sys, math
for mod in list(sys.modules.keys()):
    if 'content' in mod or 'data_loader' in mod or 'strength' in mod or 'player' in mod:
        del sys.modules[mod]

from content_automation import GLOBAL_GF, GLOBAL_GA, RESULTS_DF, TEAM_RATINGS, get_team_stats
from strength_adjust import get_adjusted_stats
from data_loader import get_team_ranking
from player_impact import get_team_star_impact

print(f"GLOBAL_GF: {GLOBAL_GF:.3f}")
print(f"GLOBAL_GA: {GLOBAL_GA:.3f}")

pairs = [('Argentina', 'Brazil'), ('Spain', 'Germany')]

for home, away in pairs:
    print(f"\n{'='*50}")
    print(f"  {home} vs {away}")
    print(f"{'='*50}")
    
    hs = get_team_stats(RESULTS_DF, home)
    as_ = get_team_stats(RESULTS_DF, away)
    
    h_adj = get_adjusted_stats(RESULTS_DF, home, TEAM_RATINGS)
    a_adj = get_adjusted_stats(RESULTS_DF, away, TEAM_RATINGS)
    
    h_gf_raw = h_adj['blended_gf'] if h_adj else hs['avg_gf']
    h_ga_raw = h_adj['blended_ga'] if h_adj else hs['avg_ga']
    a_gf_raw = a_adj['blended_gf'] if a_adj else as_['avg_gf']
    a_ga_raw = a_adj['blended_ga'] if a_adj else as_['avg_ga']
    
    # Shrinkage
    shrink_k = 10
    h_n = hs['n_matches']
    a_n = as_['n_matches']
    h_gf = (h_n * h_gf_raw + shrink_k * GLOBAL_GF) / (h_n + shrink_k)
    h_ga = (h_n * h_ga_raw + shrink_k * GLOBAL_GA) / (h_n + shrink_k)
    a_gf = (a_n * a_gf_raw + shrink_k * GLOBAL_GF) / (a_n + shrink_k)
    a_ga = (a_n * a_ga_raw + shrink_k * GLOBAL_GA) / (a_n + shrink_k)
    
    h_rank = get_team_ranking(home).get('rank', 100)
    a_rank = get_team_ranking(away).get('rank', 100)
    
    rank_diff = a_rank - h_rank
    sign = 1 if rank_diff >= 0 else -1
    log_diff = sign * math.log1p(abs(rank_diff)) * 0.10
    rank_factor = max(0.50, min(2.0, math.exp(log_diff)))
    
    rank_home_lambda = GLOBAL_GF * rank_factor
    rank_away_lambda = GLOBAL_GF / rank_factor
    
    home_lambda_raw = h_gf * (a_ga / GLOBAL_GA)
    away_lambda_raw = a_gf * (h_ga / GLOBAL_GA)
    
    rank_gap = abs(h_rank - a_rank)
    both_top = h_rank <= 30 and a_rank <= 30
    regress = 0.50 if both_top else 0.30
    
    home_lambda_form = (1 - regress) * home_lambda_raw + regress * GLOBAL_GF
    away_lambda_form = (1 - regress) * away_lambda_raw + regress * GLOBAL_GF
    
    rank_weight = min(0.65, 0.55 + rank_gap * 0.002) if both_top else min(0.65, 0.35 + rank_gap * 0.004)
    form_weight = 1.0 - rank_weight
    
    home_blend = form_weight * home_lambda_form + rank_weight * rank_home_lambda
    away_blend = form_weight * away_lambda_form + rank_weight * rank_away_lambda
    
    h_star = get_team_star_impact(home)
    a_star = get_team_star_impact(away)
    
    print(f"  {home} rank: {h_rank}, {away} rank: {a_rank}, gap: {rank_gap}")
    print(f"  both_top: {both_top}, rank_weight: {rank_weight:.2f}")
    print(f"  {home} form (after shrink): gf={h_gf:.2f} ga={h_ga:.2f}")
    print(f"  {away} form (after shrink): gf={a_gf:.2f} ga={a_ga:.2f}")
    print(f"  rank_factor: {rank_factor:.3f}")
    print(f"  rank_home_lambda: {rank_home_lambda:.3f}")
    print(f"  rank_away_lambda: {rank_away_lambda:.3f}")
    print(f"  home_lambda_raw (form): {home_lambda_raw:.3f}")
    print(f"  away_lambda_raw (form): {away_lambda_raw:.3f}")
    print(f"  after regression: home={home_lambda_form:.3f} away={away_lambda_form:.3f}")
    print(f"  after blend: home={home_blend:.3f} away={away_blend:.3f}")
    print(f"  star impact: {home}={h_star:.2f}x {away}={a_star:.2f}x")
    print(f"  after stars: home={home_blend*h_star:.3f} away={away_blend*a_star:.3f}")
    print(f"  FINAL (with home adv): home={home_blend*h_star*1.04:.3f} away={away_blend*a_star*0.96:.3f}")
