import logging

from core.load_settings import load_settings
from core.setup_logging import setup_logging

from embedding.embed_texts import embed_texts

setup_logging()
settings = load_settings()
logger = logging.getLogger("embedding")

EMBEDDING_BATCH_SIZE = settings["embedding"].get("batch_size", 32)

def batch_embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts: 
        logger.warning("No texts provided for embedding.")
        return []

    all_embeddings = []

    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start:start + EMBEDDING_BATCH_SIZE]
        batch_embeddings = embed_texts(batch)
        all_embeddings.extend(batch_embeddings)

        logger.info(f"Processed batch {start // EMBEDDING_BATCH_SIZE + 1}: {len(batch)} texts.")

        return all_embeddings
