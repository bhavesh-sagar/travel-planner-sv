from fastapi import APIRouter, BackgroundTasks
from app.models.schema import Query
from app.services.rag_service import hybrid_search
from app.services.response_service import generate_response
from app.services.cache_service import get_cache, set_cache

router = APIRouter()

@router.post("/api/ultimate-agent")
async def ultimate(q: Query, background_tasks: BackgroundTasks):

    cache_key = f"{q.user}:{q.destination.lower()}"

    cached = get_cache(cache_key)
    if cached:
        return {"cached": True, "data": cached}

    docs = hybrid_search(q.destination)
    result = generate_response(q.destination, docs)

    background_tasks.add_task(set_cache, cache_key, result)

    return {
        "data": result,
        "rag_docs": docs
    }