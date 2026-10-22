import logging
import uuid

from qdrant_client.models import PointStruct

from embedding.batch_embed_texts import batch_embed_texts

logger = logging.getLogger("vector_database")

def make_point_id(chunk: dict) -> str:
    # Qdrant chi nhan id la int hoac UUID -> tao UUID co dinh tu type + id + chunk_index
    # chay lai pipeline se ghi de point cu thay vi tao trung lap
    metadata = chunk.get("metadata", {})
    entity_id = next(
        (value for key, value in metadata.items() if (key == "id" or key.endswith("_id")) and value is not None),
        chunk["text"],  # khong co id -> dung text
    )
    key = f"{metadata.get('type', '')}:{entity_id}:{metadata.get('chunk_type', '')}:{metadata.get('chunk_index', 0)}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))

def build_qdrant_points(chunks: list[dict]) -> list[PointStruct]:
    if not chunks:
        logger.warning("No chunks provided for building Qdrant points.")
        return []

    chunks = [chunk for chunk in chunks if chunk.get("text")]
    texts = [chunk["text"] for chunk in chunks]
    if not texts:
        logger.warning("No text found in chunks for embedding.")
        return []

    embeddings = batch_embed_texts(texts)
    if not embeddings:
        logger.warning("No embeddings generated for the provided texts.")
        return []

    points = []
    for chunk, embedding in zip(chunks, embeddings):
        points.append(
            PointStruct(
                id=make_point_id(chunk),
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    **chunk.get("metadata", {}),  # Include any additional metadata if present
                },
            )
        )
    logger.info(f"Built {len(points)} Qdrant points from {len(chunks)} chunks.")

    return points
