from fastapi import APIRouter
from app.services.rag_service import hybrid_search
from app.services.cache_service import get_cache, set_cache, make_cache_key
from app.services.safety_service import check_query_safety
from app.services.response_service import humanize_response, general_chat_response
from app.services.ai_parser import parse_query

router = APIRouter()

@router.post("/api/ultimate-agent")
def agent(req: dict):
    try:
        query = req.get("destination", "").strip()
        if not query:
            return {
                "cached": False,
                "data": {},
                "text": "Please enter a valid query."
            }

        status, reason = check_query_safety(query)
        if not status and reason == "unsafe":
            return {
                "cached": False,
                "data": {},
                "text": "This request appears to involve illegal or harmful activities, which are not allowed."
            }

        cache_key = make_cache_key(query)
        cached_data = get_cache(cache_key)
        if cached_data:
            return {
                "cached": True,
                "data": cached_data.get("data", {}),
                "text": cached_data.get("text", "")
            }

        parser_key = f"parser:{query.lower()}"
        cached_parser = get_cache(parser_key)

        if cached_parser:
            print("PARSER CACHE HIT")
            parsed = cached_parser
        else:
            print("PARSER CACHE MISS")
            parsed = parse_query(query)
            set_cache(parser_key, parsed, ttl=86400)

        intent = parsed.get("intent", "general")
        location = parsed.get("location")

        if intent == "travel":
            result = hybrid_search(query, location)
            human_text = humanize_response(result)

            response = {
                "data": result,
                "text": human_text
            }
            set_cache(cache_key, response, ttl=21600)
            return {
                "cached": False,
                "data": result,
                "text": human_text
            }
        general_text = general_chat_response(query)
        response = {
            "data": {},
            "text": general_text
        }
        set_cache(cache_key, response, ttl=21600)
        return {
            "cached": False,
            "data": {},
            "text": general_text
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "cached": False,
            "data": {},
            "text": "Something went wrong while processing your request. Please try again."
        }