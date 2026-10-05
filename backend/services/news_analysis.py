import re
import urllib.parse
from typing import List, Dict, Optional

DOMAIN_WHITELIST = [
    "skysports.com",
    "bbc.co.uk",
    "theathletic.com",
    "premierleague.com",
    "fantasyfootballscout.co.uk",
    "physioroom.com",
    "nytimes.com",
    "standard.co.uk",
    "independent.co.uk",
    "telegraph.co.uk",
    "theguardian.com",
    "mirror.co.uk"
]

HEDGE_WORDS = ["might", "could", "unlikely", "doubtful whether", "expected to be assessed", "rumour", "linked with"]

# Regex families
PERMANENT_TRANSFER_REGEX = re.compile(
    r'\bsign(?:s|ed)? (?:for|with)\b|\bcompletes? (?:a |his )?(?:permanent )?move to\b|\bjoins? .* on a permanent (?:deal|transfer)\b|\bdeparts? .* on a free\b',
    re.IGNORECASE
)
LOAN_OUT_REGEX = re.compile(
    r'\bjoins? .* on (?:a .* )?loan\b|\bloan move to\b|\bloaned out to\b',
    re.IGNORECASE
)
NOT_A_LEAVE_REGEX = re.compile(
    r'\brecalled from loan\b|\blinked\b|\brumoured\b|\bcould join\b|\btarget\b',
    re.IGNORECASE
)

RED_CARD_REGEX = re.compile(
    r'\bred card(?:ed)?\b|\bsent off\b|\bstraight red\b|\bshown (?:a |the )?red\b',
    re.IGNORECASE
)

YELLOW_ACCUMULATION_REGEX = re.compile(
    r'\b(?:fourth|fifth|4th|5th) yellow\b|\baccumulat(?:ed|ion) (?:of )?(?:yellow )?(?:card|booking)s?\b',
    re.IGNORECASE
)

RECOVERED_AVAILABLE_REGEX = re.compile(
    r'\bback in training\b|\breturns? to (?:full )?training\b|\bavailable for selection\b|\bin contention (?:to start|for selection)\b|\bnamed in the squad\b|\bfitness test passed\b|\bexpected to (?:start|play|feature)\b',
    re.IGNORECASE
)

CONFIRMED_UNAVAILABLE_REGEX = re.compile(
    r'\bruled out\b|\bwill miss\b|\bsidelined (?:for|until)\b|\bundergo(?:es|ing)? surgery\b|\bout for (?:the season|\d+ weeks?)\b',
    re.IGNORECASE
)

DESTINATION_CLUB_REGEX = re.compile(r'to ([A-Z][\w\s]+?)(?:[.,]|$)', re.IGNORECASE)
BAN_MATCHES_REGEX = re.compile(r'(?:banned for|faces? a) (one|two|three|four|five|\d+)[ -]match ban', re.IGNORECASE)

def extract_real_article_url(url: str) -> str:
    if "duckduckgo.com/l/?uddg=" in url:
        try:
            parsed = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed.query)
            if 'uddg' in query_params:
                return urllib.parse.unquote(query_params['uddg'][0])
        except Exception:
            pass
    return url

def get_domain_from_url(url: str) -> str:
    try:
        domain = urllib.parse.urlparse(url).netloc
        domain = domain.replace("www.", "")
        return domain
    except:
        return ""

def get_source_name_from_domain(domain: str) -> str:
    if not domain:
        return "Web Search"
    parts = domain.split('.')
    if len(parts) >= 2:
        name = parts[0]
        if name in ['co', 'com', 'org'] and len(parts) >= 3:
            name = parts[-2]
        elif name == 'theathletic' or name == 'nytimes':
            return "The Athletic"
        elif name == 'bbc':
            return "BBC Sport"
        elif name == 'skysports':
            return "Sky Sports"
        return name.capitalize()
    return domain

def split_into_sentences(text: str) -> List[str]:
    # Very basic sentence splitting
    text = text.replace('!', '.').replace('?', '.')
    return [s.strip() for s in text.split('.') if len(s.strip()) > 5]

def classify_player_news(search_results: List[Dict], fpl_flag: str) -> Dict:
    # We will score or return the highest priority match found.
    # Priorities:
    # 1. TRANSFERRED_PERMANENT / LOANED_OUT
    # 2. RED_CARD_SUSPENSION
    # 3. YELLOW_ACCUMULATION_SUSPENSION
    # 4. RECOVERED_AVAILABLE
    # 5. CONFIRMED_UNAVAILABLE
    # 6. UNKNOWN
    
    # We will dedupe and rank results
    valid_results = []
    seen_domains = set()
    
    for r in search_results:
        raw_url = r.get('href', '')
        url = extract_real_article_url(raw_url)
        domain = get_domain_from_url(url)
        
        # Reject search engine domains
        if 'duckduckgo' in domain or 'google' in domain or 'bing' in domain:
            continue
            
        r['href'] = url
        r['domain'] = domain
        r['source_name'] = get_source_name_from_domain(domain)
        
        # Dedupe by domain
        if domain not in seen_domains:
            seen_domains.add(domain)
            valid_results.append(r)
            
    # Sort valid_results: whitelisted domains first
    valid_results.sort(key=lambda x: 0 if x['domain'] in DOMAIN_WHITELIST else 1)
    
    # Evaluate priority matches
    for category_priority in ["LEAVING", "RED_CARD", "YELLOW", "RECOVERED", "OUT"]:
        for res in valid_results:
            text = (res.get('title', '') + ". " + res.get('body', '')).replace('..', '.')
            sentences = split_into_sentences(text)
            
            for sentence in sentences:
                is_hedged = any(h in sentence.lower() for h in HEDGE_WORDS)
                confidence = "medium" if is_hedged else "high"
                
                # Check 1: Leaving
                if category_priority == "LEAVING":
                    if NOT_A_LEAVE_REGEX.search(sentence):
                        continue
                        
                    if PERMANENT_TRANSFER_REGEX.search(sentence):
                        dest_match = DESTINATION_CLUB_REGEX.search(sentence)
                        dest = dest_match.group(1).strip() if dest_match else None
                        return _build_response("TRANSFERRED_PERMANENT", "#9ca3af", "sell", -999, confidence, dest, None, res)
                    
                    if LOAN_OUT_REGEX.search(sentence):
                        dest_match = DESTINATION_CLUB_REGEX.search(sentence)
                        dest = dest_match.group(1).strip() if dest_match else None
                        return _build_response("LOANED_OUT", "#9ca3af", "sell", -999, confidence, dest, None, res)
                
                # Check 2: Red Card
                if category_priority == "RED_CARD":
                    if RED_CARD_REGEX.search(sentence):
                        ban_match = BAN_MATCHES_REGEX.search(sentence)
                        ban_matches = ban_match.group(1) if ban_match else None
                        return _build_response("RED_CARD_SUSPENSION", "#ef4444", "sell", -999, confidence, None, ban_matches, res)
                        
                # Check 3: Yellow Accumulation
                if category_priority == "YELLOW":
                    if YELLOW_ACCUMULATION_REGEX.search(sentence):
                        return _build_response("YELLOW_ACCUMULATION_SUSPENSION", "#eab308", "sell", -999, confidence, None, "1", res)
                
                # Check 4: Recovered (only if FPL flag was injured/doubtful, though we can just output it and the frontend/backend caller will see it)
                if category_priority == "RECOVERED" and fpl_flag in ['i', 'd']:
                    if RECOVERED_AVAILABLE_REGEX.search(sentence):
                        if confidence == "high":
                            return _build_response("RECOVERED_AVAILABLE", "#10b981", "keep", 999, confidence, None, None, res)
                        # If hedged, we might want to downgrade and fall through, but let's just return with medium confidence
                        # Actually the instructions say: "If one appears in the same sentence as a match, downgrade confidence to "medium" and let the raw FPL flag act as tie-breaker instead of hard classifying."
                        
                # Check 5: Confirmed Out
                if category_priority == "OUT" and fpl_flag in ['i', 'd']:
                    if CONFIRMED_UNAVAILABLE_REGEX.search(sentence):
                        return _build_response("CONFIRMED_UNAVAILABLE", "#ef4444", "sell", -999, confidence, None, None, res)

    # UNKNOWN Fallback
    # Fallback to the raw FPL flag
    if fpl_flag == 's':
        color = "#ef4444"
        decision = "sell"
        score_delta = -999
    elif fpl_flag in ['u', 'n']:
        color = "#9ca3af"
        decision = "sell"
        score_delta = -999
    elif fpl_flag == 'd':
        color = "#eab308"
        decision = "keep" # FPL defaults to keep for doubtful unless confirmed out
        score_delta = 0
    elif fpl_flag == 'i':
        color = "#ef4444"
        decision = "sell"
        score_delta = -999
    else:
        color = "#10b981"
        decision = "keep"
        score_delta = 0
        
    best_res = valid_results[0] if valid_results else None
    return _build_response("UNKNOWN", color, decision, score_delta, "low", None, None, best_res)

def _build_response(category, color, decision, score_delta, confidence, dest_club, ban_matches, res_dict):
    source_url = res_dict.get('href') if res_dict else "https://fantasy.premierleague.com"
    source_name = res_dict.get('source_name') if res_dict else "FPL Updates"
    
    return {
        "category": category,
        "color": color,
        "decision": decision,
        "score_delta": score_delta,
        "confidence": confidence,
        "destination_club": dest_club,
        "ban_matches": ban_matches,
        "source_url": source_url,
        "source_name": source_name,
        "summary": _generate_summary(category, dest_club, ban_matches)
    }

def _generate_summary(category: str, dest_club: Optional[str], ban_matches: Optional[str]) -> str:
    if category == "TRANSFERRED_PERMANENT":
        if dest_club:
            return f"{{name}} has permanently transferred to {dest_club} and is no longer available."
        return "{name} has permanently transferred to another club and is no longer available."
    elif category == "LOANED_OUT":
        if dest_club:
            return f"{{name}} has joined {dest_club} on loan and is unavailable for selection."
        return "{name} has been loaned out and is unavailable for selection."
    elif category == "RED_CARD_SUSPENSION":
        if ban_matches:
            return f"{{name}} received a red card and faces a {ban_matches}-match ban."
        return "{name} received a red card and will serve a suspension."
    elif category == "YELLOW_ACCUMULATION_SUSPENSION":
        return "{name} has accumulated too many yellow cards and will serve a one-match suspension."
    elif category == "RECOVERED_AVAILABLE":
        return "{name} has returned to full training and is expected to be available this gameweek."
    elif category == "CONFIRMED_UNAVAILABLE":
        return "{name} is confirmed to be sidelined with an injury and will miss the upcoming match."
    
    return "Recent news is speculative. The FPL status flag remains the most reliable indicator."
