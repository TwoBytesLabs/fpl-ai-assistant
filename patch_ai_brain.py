import re

with open('backend/services/analytics.py', 'r') as f:
    code = f.read()

# 1. Update score_player signature and logic
old_score = """def score_player(player: Dict, strategy: str = "next_gameweek") -> float:
    \"\"\"Calculates a heuristic score for a player based on multiple weighted factors.\"\"\"
    ep_next = float(player.get('ep_next', 0) or 0)"""
new_score = """def score_player(player: Dict, strategy: str = "next_gameweek", research_map: dict = None) -> float:
    \"\"\"Calculates a heuristic score for a player based on multiple weighted factors.\"\"\"
    
    # ── LIVE RESEARCH OVERRIDE ──
    if research_map and player.get('web_name') in research_map:
        decision = research_map[player.get('web_name')]
        if decision == 'keep':
            return 999.0  # Artificially boost to guarantee we keep them
        elif decision == 'sell':
            return -999.0 # Artificially tank to guarantee we sell them
            
    ep_next = float(player.get('ep_next', 0) or 0)"""
code = code.replace(old_score, new_score)

# 2. Update get_optimal_11
old_opt = """def get_optimal_11(squad: List[Dict], strategy: str) -> Tuple[List[Dict], List[Dict]]:
    gks = [p for p in squad if p['element_type'] == 1]
    defs = [p for p in squad if p['element_type'] == 2]
    mids = [p for p in squad if p['element_type'] == 3]
    fwds = [p for p in squad if p['element_type'] == 4]
    
    gks.sort(key=lambda x: score_player(x, strategy), reverse=True)
    defs.sort(key=lambda x: score_player(x, strategy), reverse=True)
    mids.sort(key=lambda x: score_player(x, strategy), reverse=True)
    fwds.sort(key=lambda x: score_player(x, strategy), reverse=True)"""
new_opt = """def get_optimal_11(squad: List[Dict], strategy: str, research_map: dict = None) -> Tuple[List[Dict], List[Dict]]:
    gks = [p for p in squad if p['element_type'] == 1]
    defs = [p for p in squad if p['element_type'] == 2]
    mids = [p for p in squad if p['element_type'] == 3]
    fwds = [p for p in squad if p['element_type'] == 4]
    
    gks.sort(key=lambda x: score_player(x, strategy, research_map), reverse=True)
    defs.sort(key=lambda x: score_player(x, strategy, research_map), reverse=True)
    mids.sort(key=lambda x: score_player(x, strategy, research_map), reverse=True)
    fwds.sort(key=lambda x: score_player(x, strategy, research_map), reverse=True)"""
code = code.replace(old_opt, new_opt)

# 3. Update get_best_transfers signature
old_best = """def get_best_transfers(
    starters: List[Dict], 
    bench: List[Dict], 
    all_players: List[Dict], 
    used_ids: set, 
    free_transfers: int, 
    strategy: str,
    bank_balance: float
) -> Tuple[List[Dict], List[Dict], List[TransferCard]]:
    
    squad = starters + bench"""
new_best = """def get_best_transfers(
    starters: List[Dict], 
    bench: List[Dict], 
    all_players: List[Dict], 
    used_ids: set, 
    free_transfers: int, 
    strategy: str,
    bank_balance: float,
    live_research: List[Dict] = None
) -> Tuple[List[Dict], List[Dict], List[TransferCard]]:
    
    research_map = {r['player_name']: r['decision'] for r in (live_research or [])}
    squad = starters + bench"""
code = code.replace(old_best, new_best)

# 4. Patch calls to get_optimal_11 and score_player inside get_best_transfers
# It's a bit tricky with simple replace, so I'll use regex
code = re.sub(r'get_optimal_11\(current_squad, strategy\)', r'get_optimal_11(current_squad, strategy, research_map)', code)
code = re.sub(r'score_player\(p, strategy\)', r'score_player(p, strategy, research_map)', code)
code = re.sub(r'score_player\(in_p, strategy\)', r'score_player(in_p, strategy, research_map)', code)
code = re.sub(r'score_player\(out_p, strategy\)', r'score_player(out_p, strategy, research_map)', code)
code = re.sub(r'get_optimal_11\(hypo_squad, strategy\)', r'get_optimal_11(hypo_squad, strategy, research_map)', code)

with open('backend/services/analytics.py', 'w') as f:
    f.write(code)
print("analytics.py patched")
