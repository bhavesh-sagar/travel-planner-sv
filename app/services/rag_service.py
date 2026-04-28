from app.services.response_service import generate_structured_response
from app.dependencies import qdrant
from rank_bm25 import BM25Okapi

def hybrid_search(query: str, location: str = None):
    try:
        points, _ = qdrant.scroll(collection_name="travel_data", limit=50)
        documents = [p.payload.get("text", "") for p in points]
        tokenized_docs = [doc.lower().split() for doc in documents]
        bm25 = BM25Okapi(tokenized_docs)

        query_tokens = query.lower().split()
        scores = bm25.get_scores(query_tokens)
        scored = list(zip(points, scores))
        if location:
            scored = [
                (p, s) for (p, s) in scored
                if location.lower() in p.payload.get("text", "").lower()
            ]

        scored = sorted(scored, key=lambda x: x[1], reverse=True)
        top_points = [p for p, _ in scored[:5]]

        if not top_points:
            top_points = points[:5]

        context = "\n".join([
            p.payload.get("text", "")
            for p in top_points
        ])

        if not context.strip():
            context = f"Travel info about {query}"

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