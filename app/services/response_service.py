def generate_response(city, rag_docs):

    if rag_docs:
        return {
            "summary": f"Top places in {city}",
            "places": rag_docs[:5],
            "tips": "Travel off-season for better pricing"
        }

    return {
        "summary": f"Travel ideas for {city}",
        "places": ["Popular attractions", "Local markets"],
        "tips": "Explore nearby places"
    }