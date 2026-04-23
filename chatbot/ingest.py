from __future__ import annotations

"""Ingest pages into the active vector database backend."""

import json
import re
import sys
import uuid
from typing import Any

from sentence_transformers import SentenceTransformer

from chatbot import qdrant_client as qdrant_db
from chatbot.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CLOUD_RAG,
    COLLECTION_NAME,
    EMBED_MODEL,
    PAGES_JSON_PATH,
    QDRANT_COLLECTION_NAME,
)
from chatbot.schema import create_schema
from chatbot.weaviate_client import get_client as get_weaviate_client


CATEGORY_KEYWORDS = {
    "admissions": ["admission", "apply", "eligibility", "application", "saeee", "entrance"],
    "fees": ["fee", "fees", "payment", "tuition", "cost", "scholarship"],
    "hostel": ["hostel", "accommodation", "room", "warden", "residential", "home away"],
    "programmes": ["programme", "course", "b.e", "b.tech", "m.e", "m.tech", "mca", "mba", "phd"],
    "placements": ["placement", "recruit", "internship", "industry", "career", "package"],
    "research": ["research", "publication", "patent", "phd", "r&d", "lab"],
    "campus": ["campus", "hostel", "sports", "transport", "cultural", "auditorium"],
    "about": ["vision", "mission", "chancellor", "founder", "accreditation", "naac", "nirf"],
    "faculty": ["faculty", "professor", "staff", "department", "school"],
}


def _auto_category(url: str, text: str) -> str:
    combined = (url + " " + text).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return category
    return "general"


_WHITESPACE = re.compile(r"\s{3,}")


def _clean(text: str) -> str:
    footer_idx = text.find("Connect With Us fb twit")
    if footer_idx != -1:
        text = text[:footer_idx]

    header_idx = text.find("Excellence Day - 2025")
    if header_idx != -1:
        text = text[header_idx + len("Excellence Day - 2025") :]
    else:
        header_idx_2 = text.find("Times All India Engineering Institutes Rankings")
        if header_idx_2 != -1:
            text = text[header_idx_2 + 60 :]

    text = _WHITESPACE.sub(" ", text)
    return text.strip()


def _chunk(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    start = 0
    step = size - overlap
    while start < len(words):
        end = start + size
        chunks.append(" ".join(words[start:end]))
        start += step
    return chunks


def _iter_chunk_payloads(pages: list[dict]) -> list[dict]:
    payloads: list[dict] = []
    for page in pages:
        url = page.get("url", "")
        raw = page.get("content", "")
        clean = _clean(raw)

        if len(clean.split()) < 20:
            continue

        category = _auto_category(url, clean)
        chunks = _chunk(clean)

        for idx, chunk_text in enumerate(chunks):
            if len(chunk_text.strip()) < 30:
                continue

            payloads.append(
                {
                    "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{url}#{idx}")),
                    "content": chunk_text,
                    "url": url,
                    "category": category,
                    "chunk_index": idx,
                }
            )

    return payloads


def _ingest_weaviate(embedder: SentenceTransformer, payloads: list[dict], force: bool) -> None:
    client = get_weaviate_client()
    create_schema(client)
    collection = client.collections.get(COLLECTION_NAME)

    if force:
        print("[ingest] Force mode: deleting existing Weaviate objects...")
        client.collections.delete(COLLECTION_NAME)
        create_schema(client)
        collection = client.collections.get(COLLECTION_NAME)

    count_resp = collection.aggregate.over_all(total_count=True)
    existing = count_resp.total_count or 0
    if existing > 0 and not force:
        print(f"[ingest] Weaviate already has {existing} objects. Use --force to re-ingest.")
        client.close()
        return

    total_chunks = 0
    with collection.batch.dynamic() as batch:
        for item in payloads:
            vector = embedder.encode(item["content"]).tolist()
            batch.add_object(
                properties={
                    "content": item["content"],
                    "url": item["url"],
                    "category": item["category"],
                    "chunk_index": item["chunk_index"],
                },
                vector=vector,
                uuid=item["id"],
            )
            total_chunks += 1

    print(f"[ingest] Weaviate ingest complete: {total_chunks} chunks.")
    client.close()


def _ingest_qdrant(embedder: SentenceTransformer, payloads: list[dict], force: bool) -> None:
    try:
        from qdrant_client.http import models as qmodels
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "qdrant-client is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    vector_size = embedder.get_sentence_embedding_dimension()
    qdrant_db.ensure_collection(vector_size=vector_size, recreate=force)
    client = qdrant_db.get_client()

    existing = client.count(collection_name=QDRANT_COLLECTION_NAME, exact=True).count
    if existing > 0 and not force:
        print(f"[ingest] Qdrant already has {existing} points. Use --force to re-ingest.")
        qdrant_db.close_client()
        return

    points: list[Any] = []
    total_chunks = 0
    for item in payloads:
        vector = embedder.encode(item["content"]).tolist()
        points.append(
            qmodels.PointStruct(
                id=item["id"],
                vector=vector,
                payload={
                    "content": item["content"],
                    "url": item["url"],
                    "category": item["category"],
                    "chunk_index": item["chunk_index"],
                },
            )
        )
        total_chunks += 1

        if len(points) >= 128:
            client.upsert(collection_name=QDRANT_COLLECTION_NAME, points=points, wait=True)
            points = []

    if points:
        client.upsert(collection_name=QDRANT_COLLECTION_NAME, points=points, wait=True)

    print(f"[ingest] Qdrant ingest complete: {total_chunks} chunks.")
    qdrant_db.close_client()


def ingest(force: bool = False) -> None:
    print(f"[ingest] Loading embedder: {EMBED_MODEL}")
    embedder = SentenceTransformer(EMBED_MODEL)

    print(f"[ingest] Reading: {PAGES_JSON_PATH}")
    with open(PAGES_JSON_PATH, encoding="utf-8") as f:
        pages = json.load(f)

    payloads = _iter_chunk_payloads(pages)
    print(f"[ingest] Prepared {len(payloads)} chunks from {len(pages)} pages.")

    if CLOUD_RAG:
        print("[ingest] Backend selected: Weaviate Cloud")
        _ingest_weaviate(embedder=embedder, payloads=payloads, force=force)
    else:
        print("[ingest] Backend selected: Qdrant")
        _ingest_qdrant(embedder=embedder, payloads=payloads, force=force)


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    ingest(force=force_flag)
