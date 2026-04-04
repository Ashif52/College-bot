"""Qdrant client helpers for local/cloud usage."""

from typing import Any

from chatbot.config import (
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
    QDRANT_LOCAL_PATH,
    QDRANT_URL,
)

_client: Any | None = None


def _require_qdrant() -> tuple[Any, Any]:
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http import models as qmodels
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "qdrant-client is not installed. Run `pip install -r requirements.txt`."
        ) from exc
    return QdrantClient, qmodels


def get_client() -> Any:
    """Return a singleton Qdrant client (cloud if URL is set, otherwise local)."""
    global _client
    if _client is not None:
        return _client

    QdrantClient, _ = _require_qdrant()

    if QDRANT_URL:
        _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None, timeout=30)
        print("[qdrant] Connected to remote Qdrant.")
    else:
        _client = QdrantClient(path=QDRANT_LOCAL_PATH)
        print(f"[qdrant] Local Qdrant ready at: {QDRANT_LOCAL_PATH}")

    return _client


def ensure_collection(vector_size: int, recreate: bool = False) -> None:
    """Create the collection if missing, or recreate when requested."""
    _, qmodels = _require_qdrant()
    client = get_client()

    if recreate and client.collection_exists(QDRANT_COLLECTION_NAME):
        client.delete_collection(QDRANT_COLLECTION_NAME)

    if not client.collection_exists(QDRANT_COLLECTION_NAME):
        client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE,
            ),
        )
        print(f"[qdrant] Created collection '{QDRANT_COLLECTION_NAME}'.")


def close_client() -> None:
    """Drop local singleton reference (safe no-op for remote client)."""
    global _client
    _client = None
