import re

with open('backend/services/analytics.py', 'r') as f:
    analytics = f.read()

# Update run_live_research to include a 'color' attribute
old_research = """            if yellows == 4 and status == 'a':
                decision = "keep"
                source = "FPL Stats"
                headline = f"Yellow Card Warning: {name}\""""

new_research = """            color = "#10b981" # Default green
            
            if yellows == 4 and status == 'a':
                decision = "keep"
                color = "#eab308" # Yellow
                source = "FPL Stats"
                headline = f"Yellow Card Warning: {name}\""""

analytics = analytics.replace(old_research, new_research)

old_d = """            elif status == 'd' or (chance is not None and chance > 0 and chance < 100):
                decision = "keep"
                source = "The Athletic\""""
new_d = """            elif status == 'd' or (chance is not None and chance > 0 and chance < 100):
                decision = "keep"
                color = "#eab308" # Yellow
                source = "The Athletic\""""
analytics = analytics.replace(old_d, new_d)

old_s = """            elif status == 's':
                decision = "sell"
                source = "Sky Sports\""""
new_s = """            elif status == 's':
                decision = "sell"
                color = "#ef4444" # Red
                source = "Sky Sports\""""
analytics = analytics.replace(old_s, new_s)

old_u = """            elif status in ['u', 'n']:
                decision = "sell"
                source = "Fabrizio Romano\""""
new_u = """            elif status in ['u', 'n']:
                decision = "sell"
                color = "#9ca3af" # Grey
                source = "Fabrizio Romano\""""
analytics = analytics.replace(old_u, new_u)

old_else = """            else:
                decision = "sell"
                source = "BBC Sport\""""
new_else = """            else:
                decision = "sell"
                color = "#ef4444" # Red
                source = "BBC Sport\""""
analytics = analytics.replace(old_else, new_else)

old_append = """                "details": details,
                "url": url
            })"""
new_append = """                "details": details,
                "url": url,
                "color": color
            })"""
analytics = analytics.replace(old_append, new_append)

with open('backend/services/analytics.py', 'w') as f:
    f.write(analytics)
    
print("Updated analytics.py with colors")
