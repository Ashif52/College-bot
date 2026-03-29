# chatbot/ingest.py
# ─────────────────────────────────────────────────────────────────────────────
# Reads pages.json, cleans content, chunks it, embeds with sentence-transformers
# and stores everything in Weaviate.
#
# Usage:
#   python -m chatbot.ingest
# ─────────────────────────────────────────────────────────────────────────────

import json
import re
import sys
import uuid

import weaviate
import weaviate.classes as wvc
from sentence_transformers import SentenceTransformer

from chatbot.config import (
    COLLECTION_NAME,
    EMBED_MODEL,
    PAGES_JSON_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    WEAVIATE_MODE,
    WEAVIATE_URL,
    WEAVIATE_API_KEY,
    WEAVIATE_DATA_PATH,
)
from chatbot.schema import create_schema
from chatbot.weaviate_client import get_client


# ── Category auto-tagger ───────────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "admissions":  ["admission", "apply", "eligibility", "application", "saeee", "entrance"],
    "fees":        ["fee", "fees", "payment", "tuition", "cost", "scholarship"],
    "hostel":      ["hostel", "accommodation", "room", "warden", "residential", "home away"],
    "programmes":  ["programme", "course", "b.e", "b.tech", "m.e", "m.tech", "mca", "mba", "phd"],
    "placements":  ["placement", "recruit", "internship", "industry", "career", "package"],
    "research":    ["research", "publication", "patent", "phd", "r&d", "lab"],
    "campus":      ["campus", "hostel", "sports", "transport", "cultural", "auditorium"],
    "about":       ["vision", "mission", "chancellor", "founder", "accreditation", "naac", "nirf"],
    "faculty":     ["faculty", "professor", "staff", "department", "school"],
}


def _auto_category(url: str, text: str) -> str:
    combined = (url + " " + text).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return category
    return "general"


_WHITESPACE = re.compile(r"\s{3,}")

def _clean(text: str) -> str:
    # 1. Strip everything after the massive footer starts
    footer_idx = text.find("Connect With Us fb twit")
    if footer_idx != -1:
        text = text[:footer_idx]
        
    # 2. Strip the massive top navigation menu by finding its end marker
    header_idx = text.find("Excellence Day - 2025")
    if header_idx != -1:
        text = text[header_idx + len("Excellence Day - 2025"):]
    else:
        # Fallback marker
        header_idx_2 = text.find("Times All India Engineering Institutes Rankings")
        if header_idx_2 != -1:
            text = text[header_idx_2 + 60:]

    text = _WHITESPACE.sub(" ", text)
    return text.strip()


# ── Chunker ────────────────────────────────────────────────────────────────────
def _chunk(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words   = text.split()
    chunks  = []
    start   = 0
    step    = size - overlap
    while start < len(words):
        end = start + size
        chunks.append(" ".join(words[start:end]))
        start += step
    return chunks


# ── Main ingestion ─────────────────────────────────────────────────────────────
def ingest(force: bool = False) -> None:
    print(f"[ingest] Loading embedder: {EMBED_MODEL}")
    embedder = SentenceTransformer(EMBED_MODEL)

    print(f"[ingest] Reading: {PAGES_JSON_PATH}")
    with open(PAGES_JSON_PATH, encoding="utf-8") as f:
        pages = json.load(f)

    client = get_client()
    create_schema(client)

    collection = client.collections.get(COLLECTION_NAME)

    # Optionally wipe and re-ingest
    if force:
        print("[ingest] Force mode: deleting existing objects…")
        client.collections.delete(COLLECTION_NAME)
        create_schema(client)
        collection = client.collections.get(COLLECTION_NAME)

    # Check existing count
    count_resp = collection.aggregate.over_all(total_count=True)
    existing   = count_resp.total_count or 0
    if existing > 0 and not force:
        print(f"[ingest] Collection already has {existing} objects. Use --force to re-ingest.")
        client.close()
        return

    total_chunks = 0
    with collection.batch.dynamic() as batch:
        for page in pages:
            url   = page.get("url", "")
            raw   = page.get("content", "")
            clean = _clean(raw)

            if len(clean.split()) < 20:
                continue   # skip nearly-empty pages

            category = _auto_category(url, clean)
            chunks   = _chunk(clean)

            for idx, chunk_text in enumerate(chunks):
                if len(chunk_text.strip()) < 30:
                    continue

                vector = embedder.encode(chunk_text).tolist()
                batch.add_object(
                    properties={
                        "content":     chunk_text,
                        "url":         url,
                        "category":    category,
                        "chunk_index": idx,
                    },
                    vector=vector,
                    uuid=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{url}#{idx}")),
                )
                total_chunks += 1

    print(f"[ingest] ✓ Ingested {total_chunks} chunks from {len(pages)} pages.")
    client.close()


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    ingest(force=force_flag)
