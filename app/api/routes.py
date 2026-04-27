from fastapi import APIRouter
from app.services.rag_service import hybrid_search
from app.services.cache_service import get_cache, set_cache, make_cache_key
from app.services.safety_service import check_query_safety
from app.services.response_service import humanize_response

router = APIRouter()

@router.post("/api/ultimate-agent")
def agent(req: dict):
    try:
        query = req.get("destination", "")
        if not query:
            return {"error": "No query provided"}

        status, reason = check_query_safety(query)
        try:
            if not status:
                if reason == "unsafe":
                    return {
                        "cached": False,
                        "data": {},
                        "text": "This request appears to involve illegal or harmful activities, which are not allowed. Please avoid asking such queries."
                    }

                if reason == "non_travel":
                    return {
                        "cached": False,
                        "data": {},
                        "text": "Sorry, I can only assist with safe travel-related queries."
                    }
        except Exception as e:
            return {
                "cached": False,
                "data": {},
                "text": "Unable to process your request."
            }

        cache_key = make_cache_key(query)
        cached_data = get_cache(cache_key)
        if cached_data:
            return {
                "cached": True,
                "data": cached_data["data"],
                "text": cached_data["text"]
            }

        result = hybrid_search(query)
        human_text = humanize_response(result)
        response = {
            "data": result,
            "text": human_text
        }
        set_cache(cache_key, response, ttl=3600)

        return {
            "cached": False,
            "data": result,
            "text": human_text
        }
    except Exception as e:
        print("Error:", str(e))
        return {
            "cached": False,
            "data": {},
            "text": "An error occurred while processing your request."
        }