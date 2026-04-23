"""Helpers for user-facing text cleanup and branding."""

from __future__ import annotations

import re


COLLEGE_NAME = "Nexus Institute of Technology"
COLLEGE_SHORT_NAME = "Nexus"
GENERIC_CONTACT_REPLY = "Please contact the admissions office for confirmation."

_COLLEGE_PATTERNS = (
    r"\bSathyabama Institute of Science and Technology\b",
    r"\bSathyabama Institute\b",
    r"\bSathyabama\b",
)


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def apply_public_branding(text: str) -> str:
    cleaned = text or ""
    for pattern in _COLLEGE_PATTERNS:
        cleaned = re.sub(pattern, COLLEGE_NAME, cleaned, flags=re.IGNORECASE)
    return cleaned


def strip_public_links_and_citations(text: str) -> str:
    cleaned = text or ""
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    cleaned = re.sub(r"www\.\S+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\(Source:.*?\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[\d+\]", "", cleaned)
    cleaned = re.sub(r"\bsource\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    return clean_whitespace(cleaned).strip(" -")


def sanitize_public_reply(
    text: str,
    *,
    max_sentences: int | None = None,
    max_chars: int | None = None,
) -> str:
    cleaned = apply_public_branding(strip_public_links_and_citations(text))
    if max_sentences:
        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        cleaned = " ".join(part for part in parts[:max_sentences] if part).strip()
    if max_chars and len(cleaned) > max_chars:
        cleaned = cleaned[: max_chars - 1].rstrip(",;: ") + "."
    return clean_whitespace(cleaned)
