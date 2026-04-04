# chatbot/generator.py
# ─────────────────────────────────────────────────────────────────────────────
# LLM answer generator.
#
# Provider is controlled by LLM_PROVIDER in .env:
#   "groq"   → Groq API (llama-3.3-70b-versatile, FREE)
#   "openai" → OpenAI API (gpt-4o-mini, PAID)
#
# Easy switch: change LLM_PROVIDER=openai in .env — no code change needed.
# ─────────────────────────────────────────────────────────────────────────────

from chatbot.config import (
    LLM_PROVIDER,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    SYSTEM_PROMPT,
)
from chatbot.retriever import RetrievedChunk


def _build_context(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a numbered context block."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[{i}] (Source: {chunk.url})\n{chunk.content}")
    return "\n\n".join(parts)


def _build_messages(
    question: str,
    chunks: list[RetrievedChunk],
    system_prompt: str = SYSTEM_PROMPT,
) -> list[dict]:
    context = _build_context(chunks)
    user_content = (
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_content},
    ]


def generate(
    question: str,
    chunks: list[RetrievedChunk],
    system_prompt: str = SYSTEM_PROMPT,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> str:
    """
    Generate an answer using the configured LLM provider.
    Raises ValueError if provider is unknown or API key is missing.
    """
    messages = _build_messages(question, chunks, system_prompt=system_prompt)

    if LLM_PROVIDER == "groq":
        return _generate_groq(messages, max_tokens=max_tokens, temperature=temperature)
    elif LLM_PROVIDER == "openai":
        return _generate_openai(messages, max_tokens=max_tokens, temperature=temperature)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER='{LLM_PROVIDER}'. "
            "Set LLM_PROVIDER to 'groq' or 'openai' in your .env file."
        )


# ── Groq backend (free llama) ──────────────────────────────────────────────────
def _generate_groq(messages: list[dict], max_tokens: int, temperature: float) -> str:
    from groq import Groq

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in .env")

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


# ── OpenAI backend (paid fallback) ────────────────────────────────────────────
def _generate_openai(messages: list[dict], max_tokens: int, temperature: float) -> str:
    from openai import OpenAI

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in .env")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
