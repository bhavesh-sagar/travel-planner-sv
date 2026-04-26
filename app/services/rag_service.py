from app.dependencies import qdrant, embed_model
from app.services.ner_service import extract_location

def hybrid_search(query):
    try:
        location = extract_location(query)
        vector = embed_model.encode(query).tolist()

        results = qdrant.query_points(
            collection_name="travel_data",
            query=vector,
            limit=5
        )

        return [r.payload["text"] for r in results.points]
    except Exception as e:
        print(" Qdrant failed:", str(e))
        return []