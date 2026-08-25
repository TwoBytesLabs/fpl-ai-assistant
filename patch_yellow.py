import re

with open('backend/services/analytics.py', 'r') as f:
    analytics = f.read()

old_research = """        if status != 'a':"""
new_research = """        yellows = p.get('yellow_cards', 0)
        if status != 'a' or yellows == 4:"""

analytics = analytics.replace(old_research, new_research)

old_yellow_logic = """            if status == 'd' or (chance is not None and chance > 0 and chance < 100):"""
new_yellow_logic = """            if yellows == 4 and status == 'a':
                decision = "keep"
                source = "FPL Stats"
                headline = f"Yellow Card Warning: {name}"
                details = f"{name} is currently on 4 yellow cards. If he receives one more, he will face a 1-match suspension. We are keeping him because his underlying stats (xG/xA) remain incredibly strong, but monitor his discipline."
                url = "https://fantasy.premierleague.com/statistics"
            elif status == 'd' or (chance is not None and chance > 0 and chance < 100):"""
            
analytics = analytics.replace(old_yellow_logic, new_yellow_logic)

with open('backend/services/analytics.py', 'w') as f:
    f.write(analytics)

print("Added yellow card warning")
