# chatbot/config.py
# ─────────────────────────────────────────────────────────────────────────────
# Central configuration for the RAG chatbot.
# Switch between Groq (free llama) and OpenAI by setting LLM_PROVIDER in .env
# ─────────────────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}

# ── Vector DB ──────────────────────────────────────────────────────────────────
WEAVIATE_MODE          = os.getenv("WEAVIATE_MODE", "embedded")          # "embedded" | "cloud"
WEAVIATE_URL           = os.getenv("WEAVIATE_URL", "kvl1ezdushmhtf6ymyeuqg.c0.asia-southeast1.gcp.weaviate.cloud")
WEAVIATE_API_KEY       = os.getenv("WEAVIATE_API_KEY", "TlRhWG5neGU2NGJ6eUtJR184RlNKWmJjU1BlMGVjNldyZ1BiT1QzUm9vazR6YktkTFlzditoMW9ieDVjPV92MjAw")
WEAVIATE_DATA_PATH     = os.getenv("WEAVIATE_DATA_PATH", "./chatbot/weaviate_data")

# Cloud RAG switch:
#   True  -> use Weaviate Cloud (existing flow)
#   False -> use Qdrant
CLOUD_RAG              = _as_bool(os.getenv("CLOUD_RAG", os.getenv("cloud_rag")), default=True)

# Qdrant settings (used when CLOUD_RAG=False)
QDRANT_URL             = os.getenv("QDRANT_URL", "")  # if empty, local on-disk Qdrant is used
QDRANT_API_KEY         = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "SathyabamaPage")
QDRANT_LOCAL_PATH      = os.getenv("QDRANT_LOCAL_PATH", "./chatbot/qdrant_data")

# Voicebot callbacks / dialing defaults
VOICE_PUBLIC_BASE_URL   = os.getenv("VOICE_PUBLIC_BASE_URL", "")
VOICE_DEFAULT_COUNTRY_CODE = os.getenv("VOICE_DEFAULT_COUNTRY_CODE", "+91")

# ── Embedding model (local, free) ──────────────────────────────────────────────
EMBED_MODEL            = "sentence-transformers/all-MiniLM-L6-v2"

# ── Weaviate collection name ───────────────────────────────────────────────────
COLLECTION_NAME        = "SathyabamaPage"

# ── LLM Provider: "groq" (default, free llama) | "openai" ─────────────────────
LLM_PROVIDER           = os.getenv("LLM_PROVIDER", "groq")

# ── Groq settings (free tier) ─────────────────────────────────────────────────
GROQ_API_KEY           = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL             = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # free, very capable

# ── OpenAI settings (paid fallback) ───────────────────────────────────────────
OPENAI_API_KEY         = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL           = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── RAG settings ──────────────────────────────────────────────────────────────
TOP_K_RESULTS          = int(os.getenv("RAG_TOP_K", "5"))
CHUNK_SIZE             = int(os.getenv("RAG_CHUNK_SIZE", "500"))
CHUNK_OVERLAP          = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))

# ── Source data ───────────────────────────────────────────────────────────────
PAGES_JSON_PATH        = os.getenv(
    "PAGES_JSON_PATH",
    "./sathyabama_rag/data/pages.json"
)

# ── System prompt for the chatbot ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are a friendly and helpful student enquiry assistant for 
Sathyabama Institute of Science and Technology, Chennai.

Answer ONLY using the context provided below. If the context does not contain 
enough information to answer the question, say: 
"I'm sorry, I don't have that information. Please contact the admissions office 
at 044-24503150 or visit www.sathyabama.ac.in"

Keep answers concise, factual and student-friendly. Do not make up information.
Always mention the source URL when it is helpful.
"""
