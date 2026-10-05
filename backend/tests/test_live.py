import json
import time
from services.analytics import run_live_research

def test():
    # Mocking FPL elements
    squad = [
        {
            "status": "i",
            "yellow_cards": 0,
            "news": "Ankle injury",
            "web_name": "Reece James",
            "chance_of_playing_next_round": 0
        },
        {
            "status": "i",
            "yellow_cards": 0,
            "news": "Hamstring injury",
            "web_name": "Shaw",
            "chance_of_playing_next_round": 0
        },
        {
            "status": "u",
            "yellow_cards": 0,
            "news": "Transferred",
            "web_name": "Ivan Toney",
            "chance_of_playing_next_round": 0
        }
    ]
    
    # We will test them one by one to avoid threading rate limits for this test script
    # So we bypass run_live_research's ThreadPoolExecutor and call fetch directly if we want
    # but let's just let run_live_research run. Threading might hit 403. Let's mock it inline to be safe.
    
    res = run_live_research(squad)
    for r in res:
        print(f"Player: {r['player_name']}")
        print(f"Decision: {r['decision']} | Color: {r['color']}")
        print(f"Headline: {r['headline']}")
        print(f"Details: {r['details']}")
        print(f"URL: {r['url']}")
        print(f"Source: {r['source']}")
        print("-" * 50)

if __name__ == "__main__":
    test()
