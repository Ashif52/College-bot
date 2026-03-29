# chatbot/weaviate_client.py
# ─────────────────────────────────────────────────────────────────────────────
# Singleton Weaviate client factory — supports both Embedded and Cloud modes.
# ─────────────────────────────────────────────────────────────────────────────

import weaviate
from weaviate.embedded import EmbeddedOptions
import weaviate.classes.init as wvi

from chatbot.config import (
    WEAVIATE_MODE,
    WEAVIATE_URL,
    WEAVIATE_API_KEY,
    WEAVIATE_DATA_PATH,
)

_client: weaviate.WeaviateClient | None = None


def get_client() -> weaviate.WeaviateClient:
    """Return a connected Weaviate client (embedded or cloud)."""
    global _client

    if _client is not None and _client.is_connected():
        return _client

    if WEAVIATE_MODE == "cloud":
        if not WEAVIATE_URL:
            raise ValueError("WEAVIATE_URL must be set when WEAVIATE_MODE=cloud")
        _client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=wvi.Auth.api_key(WEAVIATE_API_KEY),
            skip_init_checks=True, # Bypasses initial gRPC timeout/firewall block
        )
        print("[weaviate] Connected to Weaviate Cloud.")
    else:
        # Default: embedded (no server needed, data stored locally)
        _client = weaviate.WeaviateClient(
            embedded_options=EmbeddedOptions(
                persistence_data_path=WEAVIATE_DATA_PATH,
            )
        )
        _client.connect()
        print(f"[weaviate] Embedded Weaviate started. Data at: {WEAVIATE_DATA_PATH}")

    return _client


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
