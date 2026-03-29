# Sathyabama Student Enquiry RAG Chatbot

A **Retrieval-Augmented Generation (RAG)** chatbot that answers student questions about Sathyabama Institute of Science and Technology using the scraped website content as its knowledge base.

## Tech Stack (Zero to Low Cost)

| Component | Tool | Cost |
|-----------|------|------|
| Vector DB | Weaviate Embedded (local) | **FREE** |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers) | **FREE** |
| LLM (default) | Groq → `llama-3.3-70b-versatile` | **FREE** |
| LLM (switch) | OpenAI `gpt-4o-mini` | ~$0.001/query |

---

## Project Structure

```
chatbot/
├── __init__.py
├── config.py          ← All settings (edit .env to tune)
├── schema.py          ← Weaviate collection definition
├── weaviate_client.py ← Embedded / Cloud client factory
├── ingest.py          ← Data pipeline: clean → chunk → embed → store
├── retriever.py       ← Semantic search in Weaviate
├── generator.py       ← LLM answer generation (Groq / OpenAI)
├── pipeline.py        ← Orchestrator: retrieve → generate
├── api.py             ← FastAPI router (mounted in main.py)
└── cli.py             ← Interactive terminal REPL
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment variables
All settings live in `.env`. The important ones for the chatbot:
```env
LLM_PROVIDER=groq          # Change to "openai" to switch LLM
GROQ_MODEL=llama-3.3-70b-versatile
WEAVIATE_MODE=embedded     # Uses local storage, no server needed
```

### 3. Run ingestion (one-time setup)
```bash
python -m chatbot.ingest
```
This will:
- Load `sathyabama_rag/data/pages.json`
- Clean the navigation boilerplate
- Split into ~500-word chunks
- Embed with `all-MiniLM-L6-v2`
- Store in local Weaviate at `chatbot/weaviate_data/`

To force re-ingest:
```bash
python -m chatbot.ingest --force
```

---

## Usage

### Option A – Interactive CLI
```bash
python -m chatbot.cli
```
Example:
```
You: What is the eligibility for MCA admission?
Bot: Searching knowledge base...
Bot: Candidates must have a Bachelor's degree in any discipline...
Sources:
  • https://www.sathyabama.ac.in/admissions/post-graduate
```

### Option B – FastAPI (via main.py)
```bash
uvicorn main:app --reload
```
Endpoints available at `http://localhost:8000`:
- `POST /chatbot/chat` — Ask a question
- `GET  /chatbot/health` — Check LLM provider
- `GET  /docs` — Swagger UI with all endpoints

Example request:
```bash
curl -X POST http://localhost:8000/chatbot/chat \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Does the college provide hostel facilities?\"}"
```

Example response:
```json
{
  "question": "Does the college provide hostel facilities?",
  "answer": "Yes, Sathyabama provides excellent hostel facilities...",
  "sources": ["https://www.sathyabama.ac.in/campus-life/hostel-facility"],
  "provider": "groq",
  "model": "llama-3.3-70b-versatile"
}
```

---

## Switching LLM Provider

**No code change needed** — just edit `.env`:

```env
# Free (default) — uses Groq's llama
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.3-70b-versatile

# Paid fallback — uses OpenAI
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
```

---

## Benchmark Questions to Test
1. *What is the eligibility for MCA admission?*
2. *What is the fee for the MCA course?*
3. *Does the college provide hostel facilities?*
4. *What sports facilities are available?*
5. *How can I apply for admission?*

---

## Weaviate Data
Vector embeddings are stored locally in `chatbot/weaviate_data/`. Delete this folder and re-run ingest if you want to start fresh.
