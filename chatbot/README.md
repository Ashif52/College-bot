# Sathyabama Student Enquiry RAG Chatbot

RAG chatbot for Sathyabama Institute queries with a switchable vector backend:

- `CLOUD_RAG=true` -> Weaviate Cloud
- `CLOUD_RAG=false` -> Qdrant (local disk by default, hosted if URL is provided)

## Tech Stack

| Component | Tool |
|---|---|
| Vector DB | Weaviate Cloud / Qdrant |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| LLM | Groq (`llama-3.3-70b-versatile`) or OpenAI (`gpt-4o-mini`) |
| API | FastAPI |

## Setup

1) Install deps

```bash
pip install -r requirements.txt
```

2) Configure `.env`

```env
# LLM
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.3-70b-versatile

# Vector backend switch
CLOUD_RAG=true

# Weaviate Cloud (used when CLOUD_RAG=true)
WEAVIATE_URL=https://<your-cluster>.weaviate.cloud
WEAVIATE_API_KEY=<your-weaviate-key>

# Qdrant (used when CLOUD_RAG=false)
# Local (default if QDRANT_URL is empty)
QDRANT_LOCAL_PATH=./chatbot/qdrant_data
# Hosted (optional)
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=SathyabamaPage

# Voicebot (Phase 2)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_NUMBER=
DEEPGRAM_API_KEY=
VOICE_PUBLIC_BASE_URL=https://<public-domain-or-ngrok>
VOICE_DEFAULT_COUNTRY_CODE=+91
```

3) Ingest data

```bash
python -m chatbot.ingest
```

Force re-ingest:

```bash
python -m chatbot.ingest --force
```

## Run API

```bash
uvicorn main:app --reload
```

Or use the helper script from the repo root to start the API, start `ngrok`, and sync `.env` automatically:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-public-api.ps1
```

For a single-terminal workflow with live logs, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-public-api-live.ps1
```

This keeps `uvicorn` and `ngrok` attached to the terminal and shuts both down when you press `Ctrl+C`.
If ngrok is installed but not on PATH, set `NGROK_PATH` to the full `ngrok.exe` path before running the script.

Useful endpoints:

- `POST /chatbot/chat`
- `GET /chatbot/health` (includes active `vector_db`)
- `GET /docs`

## Notes

- Weaviate mode stores data in your cloud cluster.
- Qdrant local mode stores vectors under `chatbot/qdrant_data/`.

