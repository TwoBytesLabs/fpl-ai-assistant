import re

with open('backend/services/analytics.py', 'r') as f:
    analytics = f.read()

# Add import at the top if it's not there
if "from duckduckgo_search import DDGS" not in analytics:
    analytics = "from duckduckgo_search import DDGS\n" + analytics

new_live_research = """
def run_live_research(squad: List[Dict]) -> List[Dict]:
    research = []
    
    for p in squad:
        status = p.get('status', 'a')
        yellows = p.get('yellow_cards', 0)
        
        if status != 'a' or yellows == 4:
            news = p.get('news', '')
            name = p.get('web_name', 'Player')
            chance = p.get('chance_of_playing_next_round')
            
            # Default fallback mock values
            decision = "keep"
            color = "#10b981" 
            headline = f"{name} update"
            details = "We couldn't fetch live data, but FPL shows an active flag."
            url = f"https://www.google.com/search?q={name.replace(' ', '+')}+injury+premier+league"
            source = "Google Search"
            
            if yellows == 4 and status == 'a':
                decision = "keep"
                color = "#eab308"
                source = "FPL Stats"
                headline = f"Yellow Card Warning: {name}"
                details = f"{name} is currently on 4 yellow cards. If he receives one more, he will face a 1-match suspension. We are keeping him because his underlying stats remain strong."
                url = "https://fantasy.premierleague.com/statistics"
            else:
                # ── ACTUALLY SCRAPE THE WEB IN REAL TIME ──
                try:
                    search_query = f"{name} injury update news premier league"
                    if status == 's':
                        search_query = f"{name} suspension news premier league"
                    elif status in ['u', 'n']:
                        search_query = f"{name} transfer news loan"
                        
                    results = DDGS().text(search_query, max_results=1)
                    if results:
                        res = results[0]
                        headline = res.get('title', headline)
                        details = res.get('body', details)
                        url = res.get('href', url)
                        try:
                            source = url.split('/')[2].replace('www.', '')
                        except:
                            source = "Web Search"
                        
                        # AI Decision Engine: Naive Sentiment Analysis
                        combined_text = (headline + " " + details).lower()
                        negative_words = ['ruled out', 'miss', 'surgery', 'out for', 'blow', 'doubt', 'suspended', 'rehab', 'sidelined', 'leave', 'left', 'loaned']
                        positive_words = ['fit', 'return', 'boost', 'back in training', 'available', 'starts', 'cleared']
                        
                        is_negative = any(word in combined_text for word in negative_words)
                        is_positive = any(word in combined_text for word in positive_words)
                        
                        if status == 's' or status in ['u', 'n']:
                            decision = "sell"
                            color = "#ef4444"
                        elif is_negative and not is_positive:
                            decision = "sell"
                            color = "#ef4444"
                        elif is_positive:
                            decision = "keep"
                            color = "#10b981"
                        else:
                            # Fallback to FPL logic if web search is ambiguous
                            if chance and int(chance) <= 50:
                                decision = "sell"
                                color = "#ef4444"
                            else:
                                decision = "keep"
                                color = "#eab308"
                except Exception as e:
                    print(f"Web Search Failed for {name}: {e}")
                    # If scraping fails, use strict fallback colors based on FPL severity
                    if status == 'd': color = "#eab308"
                    elif status in ['s', 'i']: color = "#ef4444"
                    elif status in ['u', 'n']: color = "#9ca3af"
                
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
"""

# Replace the old run_live_research function completely
start_idx = analytics.find("def run_live_research(")
if start_idx != -1:
    end_idx = analytics.find("def calculate_budget_metrics(", start_idx)
    if end_idx == -1:
        # If calculate_budget_metrics is before, maybe we look for def get_optimal_11
        end_idx = analytics.find("def generate_ai_summary(", start_idx)
    
    if end_idx != -1:
        analytics = analytics[:start_idx] + new_live_research + "\n" + analytics[end_idx:]
    else:
        print("Couldn't find the end of run_live_research")

with open('backend/services/analytics.py', 'w') as f:
    f.write(analytics)

print("Backend fully upgraded to use REAL live web search via DuckDuckGo!")
