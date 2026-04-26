import redis
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")