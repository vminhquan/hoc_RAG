import os
import yaml
from dotenv import load_dotenv

load_dotenv()

# (env var, section, key, kieu du lieu)
ENV_OVERRIDES = [
    ("APP_ENV", "app", "env", str),
    ("QDRANT_URL", "vector_database", "url", str),
    ("QDRANT_API_KEY", "vector_database", "api_key", str),
    ("QDRANT_COLLECTION_NAME", "vector_database", "collection_name", str),
    ("QDRANT_TIMEOUT", "vector_database", "timeout", int),
    ("EMBEDDING_MODEL", "embedding", "model", str),
    ("EMBEDDING_DEVICE", "embedding", "device", str),
    ("EMBEDDING_BATCH_SIZE", "embedding", "batch_size", int),
    ("LLM_PROVIDER", "llm", "provider", str),
    ("LLM_MODEL_NAME", "llm", "model_name", str),
    ("LLM_BASE_URL", "llm", "base_url", str),
    ("LLM_TEMPERATURE", "llm", "temperature", float),
    ("LLM_MAX_TOKENS", "llm", "max_tokens", int),
    ("LLM_TIMEOUT", "llm", "timeout", int),
    ("RETRIEVAL_TOP_K", "retrieval", "top_k", int),
    ("RETRIEVAL_SCORE_THRESHOLD", "retrieval", "score_threshold", float),
]


def load_settings(path: str = "config/settings.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as file:
        settings = yaml.safe_load(file)

    for env_name, section, key, cast in ENV_OVERRIDES:
        value = os.getenv(env_name)
        if value:
            settings.setdefault(section, {})[key] = cast(value)

    return settings
