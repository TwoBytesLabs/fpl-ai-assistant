import traceback
import time
from duckduckgo_search import DDGS

def run_query(query_str, label):
    print(f"\n--- {label} ---")
    print(f"Query: '{query_str}'")
    try:
        results = DDGS().text(query_str, max_results=6)
        # DDGS().text returns a generator in newer versions, but we used list() in analytics
        res_list = list(results)
        print(f"Success! Type returned: {type(res_list)}, Length: {len(res_list)}")
        if res_list:
            print(f"First result title: {res_list[0].get('title')}")
            print(f"First result href: {res_list[0].get('href')}")
    except Exception as e:
        print("EXCEPTION RAISED:")
        traceback.print_exc()

if __name__ == "__main__":
    query = "Ivan Toney transfer news loan"
    
    # 1. First run after a 5+ minute natural cooldown (since the last turn)
    run_query(query, "ATTEMPT 1 (Post-Cooldown)")
    
    # 2. Back-to-back run in the same process
    print("\nRunning immediately again...")
    run_query(query, "ATTEMPT 2 (Back-to-back)")
