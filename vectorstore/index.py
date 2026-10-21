import logging

from embedding.embed_texts import embed_texts

logger = logging.getLogger("vector_database")

def build_qdrant_points(chunks: list[str]) -> list[dict]:
    if not chunks:
        logger.warning("No chunks provided for building Qdrant points.")
        return []

    texts = [chunk['text'] for chunk in chunks]
    if not texts:
        logger.warning("No text found in chunks for embedding.")
        return []

    embeddings = embed_texts(texts)
    if not embeddings:
        logger.warning("No embeddings generated for the provided texts.")
        return []

    points = []
    for chunk, embedding in zip(chunks, embeddings):
        point = {
            "id": chunk['id'],
            "vector": embedding,
            "payload": {
                "text": chunk['text'],
                **chunks.get('metadata', {})  # Include any additional metadata if present
            }
        }
    logger.info(f"Built {len(points)} Qdrant points from {len(chunks)} chunks.")
    
    return points