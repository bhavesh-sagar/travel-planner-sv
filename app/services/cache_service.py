from app.dependencies import redis_client
import json

def make_cache_key(query: str):
    return f"travel:{query.strip().lower()}"
def get_cache(key):
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print("Redis get error:", str(e))
        return None
def set_cache(key, value, ttl=3600):
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print("Redis set error:", str(e))