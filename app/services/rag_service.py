from app.services.response_service import generate_structured_response
from app.services.ner_service import extract_location
from app.dependencies import qdrant

def hybrid_search(query: str):
    try:
        location = extract_location(query)
        points, _ = qdrant.scroll(collection_name="travel_data", limit=10)
        keywords = query.lower().split()
        filtered = [
            p for p in points
            if any(k in p.payload.get("text", "").lower() for k in keywords)
        ]

        if not filtered:
            print("No match found, using fallback data")
            filtered = points[:5]

        context = "\n".join([
            p.payload.get("text", "")
            for p in filtered[:5]
        ])

        if not context.strip():
            context = f"Travel information about {query}"

        return generate_structured_response(query, context)

    except Exception as e:
        print("Qdrant failed:", str(e))
        return {
            "summary": "Search failed",
            "places": [],
            "transport": {},
            "budget": "",
            "tips": "Try again"
        }