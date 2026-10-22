# Trong retriever nhận được request từ user, sau đó gọi embed_texts để tạo embedding vector cho câu truy vấn của user. Sau đó, retriever sẽ sử dụng embedding vector này để tìm kiếm các tài liệu liên quan trong cơ sở dữ liệu vector (vector database) và trả về kết quả cho user.

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from qdrant_client.http.exceptions import ResponseHandlingException

from core.load_settings import load_settings
from embedding.embed_texts import embed_texts
from core.schema import RetrieverDocument
from vectorstore.qdrant import get_qdrant_client

settings = load_settings()
logger = logging.getLogger("retriever")

RETRIEVAL_CONFIG = settings.get("retrieval", {})
COLLECTION_NAME = settings.get("vector_database", {}).get("collection_name", "default_collection")
RETRIEVAL_TOP_K = RETRIEVAL_CONFIG.get("top_k", 5)
RETRIEVAL_SCORE_THRESHOLD = RETRIEVAL_CONFIG.get("score_threshold", 0.5)

def retriever(query: str) -> list[RetrieverDocument]:
    if not query or not query.strip():
        logger.warning("Empty query received.")
        return []

    try:
        client: QdrantClient = get_qdrant_client()
        query_vector = embed_texts([query])[0]  # Lấy embedding vector cho câu truy vấn

        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=RETRIEVAL_TOP_K,
            with_payload=True,
            score_threshold=RETRIEVAL_SCORE_THRESHOLD
        )

        points: list[ScoredPoint] = response.points
        documents: list[RetrieverDocument] = []

        for point in points:
            payload = point.payload or {}
            doc = RetrieverDocument(
                id=str(point.id),
                score=point.score,
                text=payload.get("text", ""),
                metadata={key: value for key, value in payload.items() if key != "text"}
            )
            documents.append(doc)

            logger.info(f"Retrieved document: ID={doc.id}, Score={doc.score}, Text={doc.text[:30]}..., Metadata={doc.metadata}")

        return documents

    except ResponseHandlingException as e:
        logger.error(f"Error during retrieval from Qdrant: {e}")
        raise ConnectionError(f"Failed to retrieve documents from Qdrant: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during retrieval: {e}")
        return []