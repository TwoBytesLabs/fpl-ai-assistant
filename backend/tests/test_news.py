import json
from news_analysis import classify_player_news

def test_fabrications():
    cases = [
        ("Smith returns to full training and is in contention to start Saturday", "i", "RECOVERED_AVAILABLE"),
        ("Smith will undergo surgery and is ruled out for the season", "i", "CONFIRMED_UNAVAILABLE"),
        ("Smith shown a straight red card, faces a three-match ban", "a", "RED_CARD_SUSPENSION"),
        ("Smith picks up his fifth yellow card of the season, one-match ban triggered", "a", "YELLOW_ACCUMULATION_SUSPENSION"),
        ("Smith completes permanent move to Al-Nassr", "i", "TRANSFERRED_PERMANENT"),
        ("Smith joins Leeds United on a season-long loan", "a", "LOANED_OUT"),
        ("Smith linked with a move to Saudi Arabia", "a", "UNKNOWN")
    ]
    
    for body, fpl_flag, expected in cases:
        fake_result = [{"title": "News update", "body": body, "href": "https://www.bbc.co.uk/sport/football/123"}]
        res = classify_player_news(fake_result, fpl_flag)
        if res["category"] != expected:
            print(f"FAILED: Expected {expected}, Got {res['category']} for '{body}'")
            print(res)
        else:
            print(f"PASS: {expected}")
            
if __name__ == "__main__":
    test_fabrications()
