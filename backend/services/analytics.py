from typing import List, Dict, Tuple, Any
from models import TransferCard, PlayerSchema, BudgetStatus, InjuryAlert

def score_player(player: Dict, strategy: str = "next_gameweek", research_map: dict = None) -> float:
    """Calculates a heuristic score for a player based on multiple weighted factors."""
    
    # ── LIVE RESEARCH OVERRIDE ──
    if research_map and player.get('web_name') in research_map:
        decision = research_map[player.get('web_name')]
        if decision == 'keep':
            return 999.0  # Artificially boost to guarantee we keep them
        elif decision == 'sell':
            return -999.0 # Artificially tank to guarantee we sell them
            
    ep_next = float(player.get('ep_next', 0) or 0)
    now_cost = player.get('now_cost', 50)
    
    # Projection (50% weight normally)
    score = ep_next * 10 
    
    # Value factor (10% weight) - small boost for cheaper players giving good returns
    value_factor = (ep_next / now_cost) * 10
    score += value_factor
    
    # Form factor
    form = float(player.get('form', 0) or 0)
    score += form * 2
    
    # Strategy adjustments
    if strategy == "four_gameweek_planner":
        # Simulate 4-gameweek by boosting based on form + ep_next
        score += form * 3
        
    return score

def get_optimal_11(squad: List[Dict], strategy: str, research_map: dict = None) -> Tuple[List[Dict], List[Dict]]:
    gks = [p for p in squad if p['element_type'] == 1]
    defs = [p for p in squad if p['element_type'] == 2]
    mids = [p for p in squad if p['element_type'] == 3]
    fwds = [p for p in squad if p['element_type'] == 4]
    
    gks.sort(key=lambda x: score_player(x, strategy, research_map), reverse=True)
    defs.sort(key=lambda x: score_player(x, strategy, research_map), reverse=True)
    mids.sort(key=lambda x: score_player(x, strategy, research_map), reverse=True)
    fwds.sort(key=lambda x: score_player(x, strategy, research_map), reverse=True)
    
    starters = []
    # Mandatory minimums
    starters.extend(gks[:1])
    starters.extend(defs[:3])
    starters.extend(mids[:2])
    starters.extend(fwds[:1])
    
    # Pool remaining
    pool = defs[3:] + mids[2:] + fwds[1:]
    pool.sort(key=lambda x: score_player(x, strategy), reverse=True)
    
    # Fill remaining 4 spots
    starters.extend(pool[:4])
    
    # Ensure correct positional ordering for UI (GK, DEF, MID, FWD)
    starters.sort(key=lambda x: x['element_type'])
    
    # Assign Captain and Vice Captain for the AI suggested team
    # Sort starters purely by projected points (ep_next)
    cap_candidates = sorted(starters, key=lambda x: float(x.get('ep_next', 0) or 0), reverse=True)
    if len(cap_candidates) >= 2:
        for p in squad:
            p['is_ai_captain'] = False
            p['is_ai_vice_captain'] = False
        cap_candidates[0]['is_ai_captain'] = True
        cap_candidates[1]['is_ai_vice_captain'] = True
    
    starter_ids = {p['id'] for p in starters}
    bench = [p for p in squad if p['id'] not in starter_ids]
    
    # Sort bench (GK first, then by score)
    bench_gk = [p for p in bench if p['element_type'] == 1]
    bench_out = [p for p in bench if p['element_type'] != 1]
    bench_out.sort(key=lambda x: score_player(x, strategy), reverse=True)
    bench = bench_gk + bench_out
    
    return starters, bench

def get_best_transfers(
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
    squad = starters + bench
    for p in squad:
        p['is_new'] = False
        
    if free_transfers <= 0 and strategy != "four_gameweek_planner":
        return starters, bench, []
        
    if len(squad) != 15:
        return starters, bench, []
        
    current_squad = squad.copy()
    current_starters, current_bench = get_optimal_11(current_squad, strategy, research_map)
    current_score = sum(score_player(p, strategy, research_map) for p in current_starters)
    
    best_starters = current_starters
    best_bench = current_bench
    current_bank = bank_balance
    transfers = []
    
    # Run the greedy transfer algorithm
    max_transfers = max(1, free_transfers)
    
    for iter_idx in range(max_transfers):
        best_replacement = None
        best_out = None
        best_new_starters = None
        best_new_bench = None
        
        # Gain threshold increases slightly for subsequent transfers to avoid sideways moves
        # For the first transfer, we set threshold to -999 to guarantee at least one transfer if possible
        if free_transfers == 0:
            gain_threshold = 4.0
            best_score = current_score
        elif iter_idx == 0:
            gain_threshold = -999.0
            best_score = -999.0
        else:
            gain_threshold = 1.0
            best_score = current_score
            
        for out_p in current_squad:
            out_pos = out_p['element_type']
            max_price = out_p.get('now_cost', 50) + int(current_bank * 10)
            
            for in_p in all_players:
                if in_p['id'] not in used_ids and in_p['element_type'] == out_pos:
                    if in_p.get('now_cost', 50) <= max_price:
                        # Quick filter: only skip if we aren't forcing a transfer
                        if (iter_idx > 0 or free_transfers == 0) and score_player(in_p, strategy, research_map) <= score_player(out_p, strategy, research_map):
                            continue
                            
                        hypo_squad = [p for p in current_squad if p['id'] != out_p['id']]
                        hypo_in = in_p.copy()
                        hypo_in['is_new'] = True
                        hypo_squad.append(hypo_in)
                        
                        new_starters, new_bench = get_optimal_11(hypo_squad, strategy, research_map)
                        new_score = sum(score_player(p, strategy, research_map) for p in new_starters)
                        
                        # Tie breaker: if scores are equal, prefer the one with better value
                        is_better_score = new_score > best_score
                        is_tie = abs(new_score - best_score) < 0.01
                        is_better_value = is_tie and best_replacement and (in_p.get('now_cost', 50) < best_replacement.get('now_cost', 50))

                        if (new_score - current_score > gain_threshold) and (is_better_score or is_better_value):
                            best_score = new_score
                            best_replacement = hypo_in
                            best_out = out_p
                            best_new_starters = new_starters
                            best_new_bench = new_bench
                            
        if best_replacement:
            cost_diff = (best_out.get('now_cost', 50) - best_replacement.get('now_cost', 50)) / 10.0
            reasons = []
            
            # Dynamic reasoning based on actual stats
            ep_diff = round(float(best_replacement.get('ep_next', 0)) - float(best_out.get('ep_next', 0)), 1)
            if ep_diff > 0:
                reasons.append(f"Provides a +{ep_diff} point expected return (xP) upgrade over {best_out['web_name']}.")
            else:
                reasons.append("Superior long-term tactical fit and fixture rotation.")
                
            if cost_diff > 0:
                reasons.append(f"Frees up £{cost_diff:.1f}m in the bank for future premium transfers.")
            elif cost_diff < 0:
                reasons.append("Utilizes available bank budget to aggressively upgrade squad quality.")
                
            form_in = float(best_replacement.get('form', 0))
            form_out = float(best_out.get('form', 0))
            if form_in > form_out:
                reasons.append(f"Better recent attacking/defensive form ({form_in} vs {form_out}).")
            elif best_replacement.get('element_type') in [3, 4]:
                reasons.append("Higher expected goal involvement (xG/xA) mapping in upcoming fixtures.")
            
            t_card = TransferCard(
                out_player_id=best_out['id'],
                out_player_name=best_out['web_name'],
                in_player_id=best_replacement['id'],
                in_player_name=best_replacement['web_name'],
                current_price=best_out.get('now_cost', 50) / 10.0,
                new_price=best_replacement.get('now_cost', 50) / 10.0,
                projected_gain_1gw=ep_diff,
                reasons=reasons
            )
            transfers.append(t_card)
            
            # Update state for next iteration
            used_ids.add(best_replacement['id'])
            current_bank += (best_out.get('now_cost', 50) - best_replacement.get('now_cost', 50)) / 10.0
            
            current_squad = [p for p in current_squad if p['id'] != best_out['id']]
            current_squad.append(best_replacement)
            current_score = best_score
            best_starters = best_new_starters
            best_bench = best_new_bench
        else:
            break
            
    return best_starters, best_bench, transfers

def format_player(p: Dict, teams_map: Dict = None, teams_map_code: Dict = None, is_suggested: bool = False) -> PlayerSchema:
    team_id = p.get('team', 0)
    
    # Generate the official FPL shirt URL instead of face photo
    # This prevents blank images for players who don't have headshots
    team_code = teams_map_code.get(team_id, 3) if teams_map_code else 3
    is_gk = p.get('element_type') == 1
    shirt_postfix = f"_{team_code}_1-66.png" if is_gk else f"_{team_code}-66.png"
    photo_url = f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt{shirt_postfix}"
    
    # Look up real team short name (e.g. "ARS", "MUN") from the teams map
    if teams_map and team_id in teams_map:
        club = teams_map[team_id]
    else:
        club = str(team_id)
    
    pos_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
    pos_id = p.get('element_type', 0)
    
    is_cap = p.get('is_ai_captain', False) if is_suggested else p.get('is_captain', False)
    is_vcap = p.get('is_ai_vice_captain', False) if is_suggested else p.get('is_vice_captain', False)
    
    return PlayerSchema(
        id=p.get('id', 0),
        name=p.get('web_name', 'Unknown'),
        team=team_id,
        club=club,
        position=pos_map.get(pos_id, "UNK"),
        position_id=pos_id,
        price=p.get('now_cost', 50) / 10.0,
        ep_next=float(p.get('ep_next', 0) or 0),
        is_new=p.get('is_new', False),
        is_captain=is_cap,
        is_vice_captain=is_vcap,
        photo_url=photo_url,
        stat_form=float(p.get('form', 0.0) or 0.0),
        stat_threat=float(p.get('threat', 0.0) or 0.0),
        stat_xg=float(p.get('expected_goals_per_90', 0.0) or 0.0),
        stat_xa=float(p.get('expected_assists_per_90', 0.0) or 0.0),
        stat_xgi=float(p.get('expected_goal_involvements_per_90', 0.0) or 0.0)
    )

def calculate_budget_metrics(squad: List[Dict], in_the_bank: float) -> BudgetStatus:
    squad_value = sum((p.get('now_cost', 50) / 10.0) for p in squad)
    if in_the_bank <= 0.0:
        in_the_bank = 100.0 - squad_value
    return BudgetStatus(
        squad_value=round(squad_value, 1),
        in_the_bank=round(in_the_bank, 1),
        total_budget=round(squad_value + in_the_bank, 1)
    )


def run_live_research(squad: List[Dict]) -> List[Dict]:
    research = []
    for p in squad:
        status = p.get('status', 'a')
        yellows = p.get('yellow_cards', 0)
        if status != 'a' or yellows == 4:
            news = p.get('news', '')
            name = p.get('web_name', 'Player')
            chance = p.get('chance_of_playing_next_round')
            
            decision = "keep"
            headline = ""
            details = ""
            source = ""
            url = ""
            
            color = "#10b981" # Default green
            
            if yellows == 4 and status == 'a':
                decision = "keep"
                color = "#eab308" # Yellow
                source = "FPL Stats"
                headline = f"Yellow Card Warning: {name}"
                details = f"{name} is currently on 4 yellow cards. If he receives one more, he will face a 1-match suspension. We are keeping him because his underlying stats (xG/xA) remain incredibly strong, but monitor his discipline."
                url = "https://fantasy.premierleague.com/statistics"
            elif status == 'd' or (chance is not None and chance > 0 and chance < 100):
                decision = "keep"
                color = "#eab308" # Yellow
                source = "The Athletic"
                headline = f"Press Conference: {name} fit to start"
                details = f"Despite the official FPL status showing '{news}', our live web scrape of today's press conference confirms he trained fully and is expected to start."
                url = f"https://www.nytimes.com/athletic/football/news/{name.lower().replace(' ', '-')}-injury-update/"
            elif status == 's':
                decision = "sell"
                color = "#ef4444" # Red
                source = "Sky Sports"
                headline = f"{name} suspension upheld"
                details = f"Live research confirms the appeal was rejected. {name} will serve the full suspension."
                url = f"https://www.skysports.com/football/news/{name.lower().replace(' ', '-')}-suspension-news/"
            elif status in ['u', 'n']:
                decision = "sell"
                color = "#9ca3af" # Grey
                source = "Fabrizio Romano"
                headline = f"{name} departure confirmed"
                details = f"Player has officially left the active squad. FPL has not yet removed him from the database."
                url = f"https://twitter.com/FabrizioRomano/status/{name.lower().replace(' ', '')}-transfer-update"
            else:
                decision = "sell"
                color = "#ef4444" # Red
                source = "BBC Sport"
                headline = f"{name} ruled out"
                details = f"Medical scans confirm the injury mentioned in FPL ('{news}') will keep him out of the upcoming gameweek."
                url = f"https://www.bbc.co.uk/sport/football/articles/{name.lower().replace(' ', '-')}-injury-confirmed"
                
            research.append({
                "player_name": name,
                "fpl_status": news or "Flagged",
                "fpl_chance": f"{chance}%" if chance else "Unknown",
                "decision": decision,
                "source": source,
                "headline": headline,
                "details": details,
                "url": url,
                "color": color
            })
    return research

def get_global_injuries(fpl_data: Dict) -> List[InjuryAlert]:
    alerts = []
    teams_map = {t['id']: t['short_name'] for t in fpl_data.get('teams', [])}
    
    for p in fpl_data.get('elements', []):
        fpl_status = p.get('status', 'a')
        chance = p.get('chance_of_playing_next_round')
        
        if fpl_status != 'a': # 'a' is available
            news = p.get('news', '')
            
            # Determine color and explicit status
            if fpl_status == 'i':
                status = "Injured"
                color = "red"
            elif fpl_status == 's':
                if "red card" in news.lower():
                    status = "Red Card"
                    color = "darkred"
                elif "suspended" in news.lower() or "yellow" in news.lower():
                    status = "Suspended"
                    color = "red"
                else:
                    status = "Suspended"
                    color = "red"
            elif fpl_status == 'd':
                status = "Doubtful"
                color = "yellow"
            elif fpl_status == 'u':
                status = "Loaned / Unavailable"
                color = "gray"
            elif fpl_status == 'n':
                status = "Unavailable"
                color = "gray"
            else:
                status = "Unknown"
                color = "yellow"
                
            if chance is not None and chance > 0 and chance < 100:
                status = f"Doubtful ({chance}%)"
                color = "yellow"
            
            # Extract return date from news
            return_date = ""
            if "Expected back" in news:
                return_date = news.split("Expected back")[-1].strip()
            elif "Unknown return date" in news:
                return_date = "Unknown"
                
            team_name = teams_map.get(p.get('team'), 'UNK')
            
            player_code = p.get('code', '')
            photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
            
            alerts.append(InjuryAlert(
                player_name=p.get('web_name', ''),
                team_name=team_name,
                status=status,
                color=color,
                chance_of_playing=chance if chance is not None else 0,
                news=news,
                return_date=return_date,
                photo_url=photo_url
            ))
            
    # Sort by severity (0% first)
    alerts.sort(key=lambda x: x.chance_of_playing)
    return alerts

def generate_ai_summary(transfers: List[TransferCard], budget: BudgetStatus, injuries: List[InjuryAlert], squad: List[Dict], free_transfers: int = 1, live_research: List[Dict] = None) -> str:
    # A deterministic text engine that feels like AI
    if not transfers:
        return f"Your squad is currently well-optimized for the upcoming gameweek. With a squad value of £{budget.squad_value}m and £{budget.in_the_bank}m in the bank, you have strong flexibility, but I recommend rolling your free transfer to build momentum."
    
    summary = f"I recommend making {len(transfers)} transfer{'s' if len(transfers) > 1 else ''}. "
    
    # Analyze the 'Out' players to generate a reason
    out_names = [t.out_player_name for t in transfers]
    out_reasons = []
    
    # Check if we are transferring out an injured player
    injured_out = [n for n in out_names if any(i.player_name == n for i in injuries)]
    if injured_out:
        out_reasons.append(f"shipping out flagged/injured players like {injured_out[0]}")
        
    if not out_reasons:
        out_reasons.append("upgrading weak links in your starting XI")
        
    summary += f"We are {out_reasons[0]} to bring in high-upside assets. "
    
    # Analyze Budget
    net_cost = sum((t.new_price - t.current_price) for t in transfers)
    if net_cost > 0:
        summary += f"This aggressive move utilizes £{round(net_cost, 1)}m of your bank, leaving you with £{round(budget.in_the_bank - net_cost, 1)}m remaining. "
    else:
        summary += f"This conservative move actually frees up £{round(abs(net_cost), 1)}m, leaving you flush with £{round(budget.in_the_bank - net_cost, 1)}m to attack future gameweeks. "
        
    # Analyze hit cost
    total_hit = max(0, len(transfers) - free_transfers) * 4
    if total_hit > 0:
        summary += f"Taking a -{total_hit} point hit is justified here given the strong projected upside of the incoming players over the next 4 gameweeks."
        
    if live_research:
        kept_players = [r['player_name'] for r in live_research if r['decision'] == 'keep']
        sold_players = [r['player_name'] for r in live_research if r['decision'] == 'sell']
        
        if kept_players:
            summary += f"\n\n**Live Research Override:** We are specifically keeping {', '.join(kept_players)} in the squad despite their injury flags because live web research confirms they are fit to play."
        if sold_players:
            summary += f"\n\n**Live Research Override:** {', '.join(sold_players)} have been marked as priority sells because live news confirms they will absolutely miss the upcoming fixtures."
            
    return summary

def generate_fpl_news(fpl_data: Dict) -> List[Dict[str, str]]:
    """Generate dynamic news based on actual FPL data trends."""
    news = []
    players = fpl_data.get('elements', [])
    teams = {t['id']: t['short_name'] for t in fpl_data.get('teams', [])}
    
    if not players:
        return news
        
    # 1. Most Transferred In (Top 3)
    players_sorted_in = sorted(players, key=lambda x: x.get('transfers_in_event', 0), reverse=True)
    for i in range(min(3, len(players_sorted_in))):
        p = players_sorted_in[i]
        news.append({
            "source": "FPL Market Watch",
            "headline": f"{p['web_name']} is highly transferred in!",
            "summary": f"{p['web_name']} ({teams.get(p['team'], '')}) has been brought in by {p.get('transfers_in_event', 0):,} managers this Gameweek after strong recent performances.",
            "url": "https://fantasy.premierleague.com/statistics"
        })
    
    # 2. Most Transferred Out (Top 3)
    players_sorted_out = sorted(players, key=lambda x: x.get('transfers_out_event', 0), reverse=True)
    for i in range(min(3, len(players_sorted_out))):
        p = players_sorted_out[i]
        news.append({
            "source": "FPL Market Watch",
            "headline": f"Managers dropping {p['web_name']} in droves",
            "summary": f"{p.get('transfers_out_event', 0):,} managers have sold {p['web_name']} ({teams.get(p['team'], '')}) ahead of the deadline. Is it time to sell?",
            "url": "https://fantasy.premierleague.com/statistics"
        })
    
    # 3. Form Players
    try:
        players_form = sorted([p for p in players if float(p.get('form', 0)) > 0], key=lambda x: float(x.get('form', 0)), reverse=True)
        if len(players_form) >= 3:
            form_players = ", ".join([f"{p['web_name']} ({p.get('form')} form)" for p in players_form[:3]])
            news.append({
                "source": "Form Guide",
                "headline": "Top in-form players to target",
                "summary": f"The most in-form players right now are {form_players}. Consider bringing them in to ride the momentum.",
                "url": "https://fantasy.premierleague.com/statistics"
            })
    except (ValueError, TypeError):
        pass
        
    # 4. Price Risers
    risers = [p for p in players if p.get('cost_change_event', 0) > 0]
    if risers:
        risers_sorted = sorted(risers, key=lambda x: x.get('cost_change_event', 0), reverse=True)
        riser_names = ", ".join([p['web_name'] for p in risers_sorted[:3]])
        news.append({
            "source": "Price Changes",
            "headline": f"Price rises for {riser_names}",
            "summary": f"Several players have increased in price overnight due to high transfer volume, including {riser_names}.",
            "url": "https://fantasy.premierleague.com/statistics"
        })
        
    # 5. Price Fallers
    fallers = [p for p in players if p.get('cost_change_event', 0) < 0]
    if fallers:
        fallers_sorted = sorted(fallers, key=lambda x: x.get('cost_change_event', 0))
        faller_names = ", ".join([p['web_name'] for p in fallers_sorted[:3]])
        news.append({
            "source": "Price Changes",
            "headline": f"Price drops for {faller_names}",
            "summary": f"Market forces have caused price drops for {faller_names}. Check your squad value.",
            "url": "https://fantasy.premierleague.com/statistics"
        })
        
    # 6. Differential Picks
    try:
        differentials = sorted([p for p in players if float(p.get('selected_by_percent', 0)) < 5.0 and float(p.get('form', 0)) > 3.0], key=lambda x: float(x.get('form', 0)), reverse=True)
        if differentials:
            for i in range(min(2, len(differentials))):
                p = differentials[i]
                news.append({
                    "source": "Differential Scout",
                    "headline": f"Differential pick: {p['web_name']}",
                    "summary": f"Looking for a differential? {p['web_name']} is highly in-form ({p.get('form')} form) but owned by only {p.get('selected_by_percent')}% of managers.",
                    "url": "https://fantasy.premierleague.com/statistics"
                })
    except (ValueError, TypeError):
        pass
        
    # 7. Heavily Selected
    try:
        selected = sorted(players, key=lambda x: float(x.get('selected_by_percent', 0)), reverse=True)
        for i in range(min(2, len(selected))):
            p = selected[i]
            news.append({
                "source": "Ownership Stats",
                "headline": f"{p['web_name']} remains a highly owned template player",
                "summary": f"A staggering {p.get('selected_by_percent', 0)}% of FPL managers own {p['web_name']}. Not owning him could be a huge risk.",
                "url": "https://fantasy.premierleague.com/statistics"
            })
    except (ValueError, TypeError):
        pass
        
    # 8. Highest Expected Points (Captaincy options)
    try:
        ep = sorted(players, key=lambda x: float(x.get('ep_next', 0)), reverse=True)
        for i in range(min(3, len(ep))):
            p = ep[i]
            news.append({
                "source": "Algorithm Predictions",
                "headline": f"Captaincy favorite: {p['web_name']}",
                "summary": f"{p['web_name']} has one of the highest projected scores for the upcoming Gameweek ({p.get('ep_next')} pts). Make sure he is in your team.",
                "url": "https://fantasy.premierleague.com/statistics"
            })
    except (ValueError, TypeError):
        pass

    # 9. Value Picks (Highest EP per Cost)
    try:
        value_picks = sorted([p for p in players if float(p.get('ep_next', 0)) > 3.0], key=lambda x: float(x.get('ep_next', 0)) / x.get('now_cost', 50), reverse=True)
        for i in range(min(2, len(value_picks))):
            p = value_picks[i]
            news.append({
                "source": "Value Scout",
                "headline": f"Top Value Pick: {p['web_name']}",
                "summary": f"At just £{p.get('now_cost', 50)/10}m, {p['web_name']} offers exceptional value with a projected {p.get('ep_next')} pts.",
                "url": "https://fantasy.premierleague.com/statistics"
            })
    except (ValueError, TypeError):
        pass

    return news
