import logging

from openai import OpenAI
from core.load_settings import load_settings

settings = load_settings()
logger = logging.getLogger("embedding")

EMBEDDING_MODEL = settings["embedding"]["model"]
_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        logger.info(f"Using OpenAI embedding model: {EMBEDDING_MODEL}")
        _client = OpenAI()  # doc OPENAI_API_KEY tu .env
    return _client

def embed_texts(texts: list[str]) -> list[list[float]]: # {"Câu văn 1"} = {[0.1,0.2,0.3,....]}
    if not texts:
        logger.warning("No texts provided for embedding.")
        return []

    client = get_client()
    try:
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    except Exception as e:
        logger.error(f"Embedding failed (model={EMBEDDING_MODEL}): {e}")
        raise
    embeddings = [item.embedding for item in sorted(response.data, key=lambda item: item.index)]
    logger.info(f"Generated embeddings for {len(texts)} texts.")
    return embeddings
