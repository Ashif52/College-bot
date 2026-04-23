"""Simple local FAQ store and fast-path intent routing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from chatbot.public_text import sanitize_public_reply


FAQ_DATA_PATH = Path(__file__).with_name("faq_data.json")

FAQ_INTENT_KEYWORDS = {
    "hostel": ("hostel", "accommodation", "stay", "room", "mess"),
    "fees": ("fee", "fees", "tuition", "cost", "payment", "scholarship"),
    "eligibility": ("eligibility", "eligible", "qualification", "criteria", "cutoff", "marks"),
    "counselling": ("counselling", "counseling", "quota", "management", "tnea", "tancet", "admission mode"),
}

_faq_cache: dict[str, Any] | None = None


def _normalize(text: str) -> str:
    return " ".join((text or "").lower().strip().replace("?", " ").split())


def preload_faq_data() -> dict[str, Any]:
    global _faq_cache
    if _faq_cache is None:
        with FAQ_DATA_PATH.open("r", encoding="utf-8") as handle:
            _faq_cache = json.load(handle)
    return _faq_cache


def classify_faq_intent(question: str) -> str | None:
    normalized = _normalize(question)
    if not normalized:
        return None

    for intent, keywords in FAQ_INTENT_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return intent
    return None


def _entry_matches(question: str, entry: dict[str, Any]) -> bool:
    normalized = _normalize(question)
    keywords = [_normalize(str(item)) for item in entry.get("keywords", []) if str(item).strip()]
    if keywords and any(keyword in normalized for keyword in keywords):
        return True

    sample_question = _normalize(str(entry.get("question", "")))
    return bool(sample_question and sample_question in normalized)


def lookup_faq_answer(question: str) -> tuple[str | None, str | None]:
    intent = classify_faq_intent(question)
    if not intent:
        return None, None

    data = preload_faq_data()
    for entry in data.get(intent, []):
        if not isinstance(entry, dict):
            continue
        if _entry_matches(question, entry):
            answer = sanitize_public_reply(str(entry.get("answer", "")))
            if answer:
                return intent, answer
    return intent, None
