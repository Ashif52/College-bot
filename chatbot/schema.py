# chatbot/schema.py
# ─────────────────────────────────────────────────────────────────────────────
# Defines and creates the Weaviate collection schema for SathyabamaPage.
# ─────────────────────────────────────────────────────────────────────────────

import weaviate
import weaviate.classes as wvc
from chatbot.config import COLLECTION_NAME


def create_schema(client: weaviate.WeaviateClient) -> None:
    """Create the SathyabamaPage collection if it does not already exist."""
    existing = [c.name for c in client.collections.list_all().values()]

    if COLLECTION_NAME in existing:
        print(f"[schema] Collection '{COLLECTION_NAME}' already exists — skipping creation.")
        return

    client.collections.create(
        name=COLLECTION_NAME,
        description="Chunks of Sathyabama Institute website content for RAG",
        vectorizer_config=wvc.config.Configure.Vectorizer.none(),   # we bring our own vectors
        properties=[
            wvc.config.Property(
                name="content",
                data_type=wvc.config.DataType.TEXT,
                description="The chunk of page text",
            ),
            wvc.config.Property(
                name="url",
                data_type=wvc.config.DataType.TEXT,
                description="Source URL of the page",
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="category",
                data_type=wvc.config.DataType.TEXT,
                description="Auto-derived topic tag (admissions, hostel, fees, etc.)",
                skip_vectorization=True,
            ),
            wvc.config.Property(
                name="chunk_index",
                data_type=wvc.config.DataType.INT,
                description="Index of this chunk within its source page",
                skip_vectorization=True,
            ),
        ],
    )
    print(f"[schema] Created collection '{COLLECTION_NAME}'.")
