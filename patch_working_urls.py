import re

with open('backend/services/analytics.py', 'r') as f:
    analytics = f.read()

# Update the URLs to be actual working search query URLs instead of fake article slugs

# The Athletic (NYTimes) Search
old_athletic = 'url = f"https://www.nytimes.com/athletic/football/news/{name.lower().replace(\' \', \'-\')}-injury-update/"'
new_athletic = 'url = f"https://www.nytimes.com/athletic/search/?query={name.replace(\' \', \'+\')}+injury"'
analytics = analytics.replace(old_athletic, new_athletic)

# Sky Sports Search
old_sky = 'url = f"https://www.skysports.com/football/news/{name.lower().replace(\' \', \'-\')}-suspension-news/"'
new_sky = 'url = f"https://www.skysports.com/search?q={name.replace(\' \', \'%20\')}"'
analytics = analytics.replace(old_sky, new_sky)

# Fabrizio Romano Twitter Search
old_fab = 'url = f"https://twitter.com/FabrizioRomano/status/{name.lower().replace(\' \', \'\')}-transfer-update"'
new_fab = 'url = f"https://twitter.com/search?q=from%3AFabrizioRomano%20{name.replace(\' \', \'%20\')}"'
analytics = analytics.replace(old_fab, new_fab)

# BBC Sport Search
old_bbc = 'url = f"https://www.bbc.co.uk/sport/football/articles/{name.lower().replace(\' \', \'-\')}-injury-confirmed"'
new_bbc = 'url = f"https://www.bbc.co.uk/search?q={name.replace(\' \', \'%20\')}+injury"'
analytics = analytics.replace(old_bbc, new_bbc)

with open('backend/services/analytics.py', 'w') as f:
    f.write(analytics)
    
print("Updated URLs to be real working search links!")
