from duckduckgo_search import DDGS
print(f"Total results: {len(list(DDGS().text('Arsenal', max_results=2)))}")
