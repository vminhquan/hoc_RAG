import logging

from qdrant_client import QdrantClient
from core.load_settings import load_settings
from vectorstore.index import build_qdrant_points
from vectorstore.qdrant import ensure_collection, get_qdrant_client

settings = load_settings()
logger = logging.getLogger("vector_database")

QDRANT_CONFIG = settings.get("vector_database", {})
COLLECTION_NAME = QDRANT_CONFIG.get("collection_name", "default_collection")

def upsert_chunks(chunks: list[dict]):
    if not chunks:
        logger.warning("No chunks provided for upsert.")
        return

    client: QdrantClient = get_qdrant_client()
    ensure_collection(client)

    points = build_qdrant_points(chunks)
    if not points:
        logger.warning("No points generated for upsert.")
        return

    try:
        response = client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        logger.info(f"Upserted {len(points)} points into collection '{COLLECTION_NAME}'. Response: {response}")
    except Exception as e:
        logger.error(f"Failed to upsert points into Qdrant: {e}")
        raise e