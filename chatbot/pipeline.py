# chatbot/pipeline.py
# ─────────────────────────────────────────────────────────────────────────────
# Thin orchestrator: retrieve → generate → return structured result.
# ─────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass, field

from chatbot.retriever import retrieve, RetrievedChunk
from chatbot.generator import generate
from chatbot.config import TOP_K_RESULTS


@dataclass
class RAGResponse:
    question: str
    answer:   str
    sources:  list[str]  = field(default_factory=list)
    chunks:   list[RetrievedChunk] = field(default_factory=list)


def query(question: str, top_k: int = TOP_K_RESULTS) -> RAGResponse:
    """
    Full RAG pipeline:
      1. Retrieve relevant chunks from Weaviate
      2. Generate an answer using the configured LLM
      3. Return answer + unique source URLs
    """
    chunks = retrieve(question, top_k=top_k)

    if not chunks:
        return RAGResponse(
            question=question,
            answer=(
                "I'm sorry, I couldn't find relevant information for your question. "
                "Please contact the admissions office at 044-24503150 or visit "
                "www.sathyabama.ac.in"
            ),
            sources=[],
            chunks=[],
        )

    answer = generate(question, chunks)

    # Deduplicated source URLs, preserving relevance order
    seen: set[str] = set()
    sources: list[str] = []
    for chunk in chunks:
        if chunk.url and chunk.url not in seen:
            seen.add(chunk.url)
            sources.append(chunk.url)

    return RAGResponse(
        question=question,
        answer=answer,
        sources=sources,
        chunks=chunks,
    )
