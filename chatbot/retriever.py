# chatbot/retriever.py
# ─────────────────────────────────────────────────────────────────────────────
# Semantic retrieval from Weaviate using the same embedding model as ingest.
# ─────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass
from sentence_transformers import SentenceTransformer

import weaviate.classes as wvc

from chatbot.config import COLLECTION_NAME, EMBED_MODEL, TOP_K_RESULTS
from chatbot.weaviate_client import get_client


@dataclass
class RetrievedChunk:
    content:     str
    url:         str
    category:    str
    chunk_index: int
    score:       float


# Lazy-load embedder once
_embedder: SentenceTransformer | None = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def retrieve(query: str, top_k: int = TOP_K_RESULTS) -> list[RetrievedChunk]:
    """
    Embed the query, run a near-vector search in Weaviate, and return the
    top-k most relevant chunks.
    """
    embedder   = _get_embedder()
    query_vec  = embedder.encode(query).tolist()

    client     = get_client()
    collection = client.collections.get(COLLECTION_NAME)

    results = collection.query.near_vector(
        near_vector=query_vec,
        limit=top_k,
        return_metadata=wvc.query.MetadataQuery(certainty=True),
        return_properties=["content", "url", "category", "chunk_index"],
    )

    chunks: list[RetrievedChunk] = []
    for obj in results.objects:
        props = obj.properties
        score = obj.metadata.certainty or 0.0
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
