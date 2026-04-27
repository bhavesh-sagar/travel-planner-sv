import re
from app.services.cache_service import get_cache, set_cache

UNSAFE_KEYWORDS = {
    "hack", "hacking", "exploit", "sql injection", "xss",
    "bypass", "ddos", "botnet", "phishing",
    "bomb", "explosive", "kill", "assassinate",
    "drugs", "buy drugs", "sell drugs",
    "fake id", "counterfeit", "fraud", "scam",
    "steal", "password crack"
}
UNSAFE_PATTERNS = [
    r"\bhow to (hack|bypass|break into|steal)\b",
    r"\b(make|build).*(bomb|explosive)\b",
    r"\b(crack|steal).*(password|account)\b",
    r"\b(buy|sell).*(drugs|fake id)\b",
    r"\b(ddos|botnet)\b",
]
TRAVEL_KEYWORDS = {
    "travel", "trip", "hotel", "flight", "train",
    "bus", "destination", "places", "budget", "itinerary"
}

def make_safety_key(query: str):
    return f"safety:{query.strip().lower()}"

def keyword_block(query: str) -> bool:
    ql = query.lower()

    if any(k in ql for k in UNSAFE_KEYWORDS):
        return False

    if any(re.search(p, ql) for p in UNSAFE_PATTERNS):
        return False

    return True

def is_travel_query(query: str) -> bool:
    ql = query.lower()
    return any(k in ql for k in TRAVEL_KEYWORDS)

def check_query_safety(query: str):
    try:
        cache_key = make_safety_key(query)

        cached = get_cache(cache_key)
        if cached is not None:
            return cached 

        if not keyword_block(query):
            result = (False, "unsafe")
            set_cache(cache_key, result, ttl=86400)
            return result

        if not is_travel_query(query):
            result = (False, "non_travel")
            set_cache(cache_key, result, ttl=86400)
            return result

        result = (True, "safe")
        set_cache(cache_key, result, ttl=86400)
        return result

    except Exception as e:
        print("Safety error:", str(e))
        return (False, "error")