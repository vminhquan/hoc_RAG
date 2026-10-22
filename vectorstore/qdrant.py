import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from core.load_settings import load_settings

settings = load_settings()
logger = logging.getLogger("vector_database")

VECTOR_DB_SETTINGS = settings.get("vector_database", {})
VECTOR_DB_HOST = VECTOR_DB_SETTINGS.get("host", "localhost")
VECTOR_DB_PORT = VECTOR_DB_SETTINGS.get("port", 6333)
VECTOR_DB_URL = VECTOR_DB_SETTINGS.get("url", f"http://{VECTOR_DB_HOST}:{VECTOR_DB_PORT}")
VECTOR_DB_TYPE = VECTOR_DB_SETTINGS.get("type", "qdrant")
VECTOR_DB_API_KEY = VECTOR_DB_SETTINGS.get("api_key", None)
VECTOR_DB_COLLECTION = VECTOR_DB_SETTINGS.get("collection_name", "default_collection")
VECTOR_DB_VECTOR_SIZE = VECTOR_DB_SETTINGS.get("vector_size", 1024)
VECTOR_DB_TIMEOUT = VECTOR_DB_SETTINGS.get("timeout", 30)  # seconds
VECTOR_DB_DISTANCE = VECTOR_DB_SETTINGS.get("distance", "cosine")  # cosine | dot | euclid

DISTANCES = {
    "cosine": Distance.COSINE,
    "dot": Distance.DOT,
    "euclid": Distance.EUCLID,
}

_client = None

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is not None:
        return _client

    try:
        # url
        if VECTOR_DB_URL:
            logger.info(f"Connecting to Qdrant at {VECTOR_DB_SETTINGS['url']} with API key: {'***' if VECTOR_DB_API_KEY else 'None'}")
            _client = QdrantClient(
                url=VECTOR_DB_SETTINGS["url"],
                api_key=VECTOR_DB_API_KEY,
                timeout=VECTOR_DB_TIMEOUT
            )
        else:
            logger.info(f"Connecting to Qdrant at {VECTOR_DB_HOST}:{VECTOR_DB_PORT} with API key: {'***' if VECTOR_DB_API_KEY else 'None'}")
            _client = QdrantClient(
                host=VECTOR_DB_HOST,
                port=VECTOR_DB_PORT,
                api_key=VECTOR_DB_API_KEY,
                timeout=VECTOR_DB_TIMEOUT
            )
        # test connection
        _client.get_collections()
        logger.info(f"Successfully connected to Qdrant at {VECTOR_DB_URL}")
        return _client

    
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        raise e

def ensure_collection(client: QdrantClient):
    existing_collections = [col.name for col in client.get_collections().collections]

    if VECTOR_DB_COLLECTION in existing_collections:
        logger.info(f"Collection '{VECTOR_DB_COLLECTION}' already exists.")
        return

    logger.info(f"Creating collection '{VECTOR_DB_COLLECTION}' with distance metric '{VECTOR_DB_DISTANCE}'")

    client.create_collection(
        collection_name=VECTOR_DB_COLLECTION,
        vectors_config=VectorParams(
            size=VECTOR_DB_VECTOR_SIZE,
            distance=DISTANCES[VECTOR_DB_DISTANCE],
        ),
    )

    logger.info(f"Collection '{VECTOR_DB_COLLECTION}' created successfully with distance metric '{VECTOR_DB_DISTANCE}'")