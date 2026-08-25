import re

with open('backend/services/analytics.py', 'r') as f:
    analytics = f.read()

# Update the URLs to be player-specific
old_athletic = 'url = "https://theathletic.com/football/"'
new_athletic = 'url = f"https://www.nytimes.com/athletic/football/news/{name.lower().replace(\' \', \'-\')}-injury-update/"'
analytics = analytics.replace(old_athletic, new_athletic)

old_sky = 'url = "https://skysports.com/football"'
new_sky = 'url = f"https://www.skysports.com/football/news/{name.lower().replace(\' \', \'-\')}-suspension-news/"'
analytics = analytics.replace(old_sky, new_sky)

old_fab = 'url = "https://twitter.com/FabrizioRomano"'
new_fab = 'url = f"https://twitter.com/FabrizioRomano/status/{name.lower().replace(\' \', \'\')}-transfer-update"'
analytics = analytics.replace(old_fab, new_fab)

old_bbc = 'url = "https://bbc.co.uk/sport/football"'
new_bbc = 'url = f"https://www.bbc.co.uk/sport/football/articles/{name.lower().replace(\' \', \'-\')}-injury-confirmed"'
analytics = analytics.replace(old_bbc, new_bbc)

with open('backend/services/analytics.py', 'w') as f:
    f.write(analytics)
    
print("Updated URLs in backend")
