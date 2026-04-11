"""Semantic retrieval over Weaviate Cloud or Qdrant."""

from dataclasses import dataclass

from sentence_transformers import SentenceTransformer
import weaviate.classes as wvc

from chatbot import qdrant_client as qdrant_db
from chatbot.config import (
    CLOUD_RAG,
    COLLECTION_NAME,
    EMBED_MODEL,
    QDRANT_COLLECTION_NAME,
    TOP_K_RESULTS,
)
from chatbot.weaviate_client import get_client as get_weaviate_client


@dataclass
class RetrievedChunk:
    content: str
    url: str
    category: str
    chunk_index: int
    score: float


_embedder: SentenceTransformer | None = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def prewarm_embedder_and_qdrant() -> None:
    """Best-effort preload for faster first query latency."""
    _get_embedder()
    qdrant_db.get_client()


def _retrieve_from_weaviate(query_vec: list[float], top_k: int) -> list[RetrievedChunk]:
    client = get_weaviate_client()
    collection = client.collections.get(COLLECTION_NAME)

    results = collection.query.near_vector(
        near_vector=query_vec,
        limit=top_k,
        return_metadata=wvc.query.MetadataQuery(distance=True),
        return_properties=["content", "url", "category", "chunk_index"],
    )

    chunks: list[RetrievedChunk] = []
    for obj in results.objects:
        props = obj.properties
        metadata = obj.metadata
        distance = getattr(metadata, "distance", None)
        score = 1.0 - float(distance) if distance is not None else 0.0
        chunks.append(
            RetrievedChunk(
                content=props.get("content", ""),
                url=props.get("url", ""),
                category=props.get("category", "general"),
                chunk_index=int(props.get("chunk_index", 0)),
                score=score,
            )
        )

    return chunks


def _retrieve_from_qdrant(query_vec: list[float], top_k: int) -> list[RetrievedChunk]:
    client = qdrant_db.get_client()
    if hasattr(client, "search"):
        results = client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vec,
            limit=top_k,
            with_payload=True,
        )
    elif hasattr(client, "query_points"):
        response = client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=query_vec,
            limit=top_k,
            with_payload=True,
        )
        results = getattr(response, "points", response)
    else:
        raise RuntimeError("Unsupported qdrant-client version: missing search/query_points API")

    chunks: list[RetrievedChunk] = []
    for hit in results:
        payload = hit.payload or {}
        chunks.append(
            RetrievedChunk(
                content=str(payload.get("content", "")),
                url=str(payload.get("url", "")),
                category=str(payload.get("category", "general")),
                chunk_index=int(payload.get("chunk_index", 0)),
                score=float(getattr(hit, "score", 0.0) or 0.0),
            )
        )

    return chunks


def retrieve(
    query: str,
    top_k: int = TOP_K_RESULTS,
    backend_override: str | None = None,
) -> list[RetrievedChunk]:
    """Embed the query and retrieve top chunks from the configured vector DB."""
    embedder = _get_embedder()
    query_vec = embedder.encode(query).tolist()

    if backend_override:
        backend = backend_override.strip().lower()
    else:
        backend = "weaviate" if CLOUD_RAG else "qdrant"

    if backend == "weaviate":
        return _retrieve_from_weaviate(query_vec=query_vec, top_k=top_k)
    if backend == "qdrant":
        return _retrieve_from_qdrant(query_vec=query_vec, top_k=top_k)

    raise ValueError("backend_override must be either 'weaviate' or 'qdrant'")
