"""Voicebot orchestration utilities for outbound follow-up calls."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from html import escape
from typing import Any
from urllib.parse import quote, urlparse, urlunparse

from dotenv import load_dotenv

from chatbot.config import VOICE_DEFAULT_COUNTRY_CODE, VOICE_PUBLIC_BASE_URL
from chatbot.excel_store import load_lead, update_voicebot_status
from chatbot.generator import generate
from chatbot.retriever import retrieve


YES_WORDS = {"yes", "yeah", "yep", "sure", "ok", "okay", "continue", "haan", "ha", "y"}
NO_WORDS = {"no", "nope", "nah", "stop", "end", "exit", "not now", "n"}
VOICE_QUERY_SYSTEM_PROMPT = """
You are a professional admissions voice assistant for Sathyabama Institute.

Answer only from the provided context.
Keep the reply short and natural for a phone call:
- at most 2 short sentences
- no URLs
- no source citations
- no bullet points
- no long lists
- if the answer is yes or no, begin with Yes or No

If the context is not clear enough, say you are not fully sure and that the admissions team will confirm it.
""".strip()
VOICE_QUERY_FALLBACK = (
    "I am not able to confirm that right now. "
    "Our admissions team will follow up with you shortly."
)
VOICE_REPEAT_FOLLOWUP = "Sorry, I did not catch that clearly. Please answer once more."
VOICE_REPEAT_QUERY = "Please repeat your question in one short sentence."
COMMON_QUALIFICATION_MAP = {
    "bcom": "BCom",
    "bsc": "BSc",
    "ba": "BA",
    "bca": "BCA",
    "be": "BE",
    "btech": "BTech",
    "mca": "MCA",
    "mba": "MBA",
    "msc": "MSc",
    "ma": "MA",
    "me": "ME",
    "mtech": "MTech",
    "phd": "PhD",
}
NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
}


def _get_voice_public_base_url() -> str:
    """
    Reload .env before reading the public base URL.
    This lets the live runner write VOICE_PUBLIC_BASE_URL after startup
    without requiring a server restart.
    """
    load_dotenv(override=True)
    return (os.getenv("VOICE_PUBLIC_BASE_URL") or VOICE_PUBLIC_BASE_URL or "").rstrip("/")


def _clean_spoken_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _looks_like_garbled_text(text: str) -> bool:
    cleaned = _clean_spoken_text(text)
    if not cleaned:
        return True
    if "\ufffd" in cleaned or "\x00" in cleaned:
        return True
    if re.search(r"(.)\1{10,}", cleaned):
        return True
    if re.search(r"(?:\([A-Za-z0-9\ufffd]?){8,}", cleaned):
        return True

    weird_chars = sum(
        1 for char in cleaned
        if not (char.isalnum() or char.isspace() or char in ".,?!:+-/%&()'\"")
    )
    return len(cleaned) >= 24 and weird_chars / max(len(cleaned), 1) > 0.25


def _words_to_number(text: str) -> int | None:
    tokens = re.findall(r"[a-z]+", text.lower())
    if not tokens:
        return None

    total = 0
    current = 0
    matched = False
    for token in tokens:
        if token not in NUMBER_WORDS:
            continue
        matched = True
        value = NUMBER_WORDS[token]
        if token == "hundred":
            current = max(current, 1) * value
        else:
            current += value

    if not matched:
        return None

    total += current
    return total


def _normalize_qualification_answer(answer: str) -> str | None:
    lowered = re.sub(r"[^a-z0-9+ ]", " ", answer.lower())
    lowered = re.sub(r"\s+", " ", lowered).strip()

    if not lowered:
        return None

    plus_two_patterns = (
        "plus two",
        "plus to",
        "12th",
        "twelfth",
        "higher secondary",
        "h s c",
        "hsc",
        "let s do",
        "lets do",
    )
    if any(pattern in lowered for pattern in plus_two_patterns):
        return "+2"

    tenth_patterns = ("10th", "tenth", "sslc")
    if any(pattern in lowered for pattern in tenth_patterns):
        return "10th"

    compact = re.sub(r"[^a-z0-9+]", "", lowered)
    if compact in COMMON_QUALIFICATION_MAP:
        return COMMON_QUALIFICATION_MAP[compact]

    return _clean_spoken_text(answer)


def _normalize_percentage_answer(answer: str) -> str | None:
    digit_match = re.search(r"(\d{1,3})", answer)
    value: int | None = None
    if digit_match:
        value = int(digit_match.group(1))
    else:
        value = _words_to_number(answer)

    if value is None:
        return _clean_spoken_text(answer)

    if 0 <= value <= 100:
        return f"{value}%"
    return str(value)


def _normalize_admission_mode_answer(answer: str) -> str:
    lowered = answer.lower()
    if "government" in lowered or "counselling" in lowered or "counseling" in lowered:
        return "Government quota"
    if "management" in lowered:
        return "Management quota"
    if "online" in lowered:
        return "Online"
    if "offline" in lowered:
        return "Offline"
    return _clean_spoken_text(answer)


def _normalize_followup_answer(question: str, answer: str) -> str | None:
    cleaned = _clean_spoken_text(answer)
    if not cleaned or _looks_like_garbled_text(cleaned):
        return None

    question_lower = question.lower()
    if "qualification" in question_lower or "education" in question_lower:
        return _normalize_qualification_answer(cleaned)
    if "percentage" in question_lower or "score" in question_lower or "marks" in question_lower:
        return _normalize_percentage_answer(cleaned)
    if "admission mode" in question_lower:
        return _normalize_admission_mode_answer(cleaned)
    if question_lower.startswith("do you ") or "hostel" in question_lower or "entrance exam" in question_lower:
        intent = parse_yes_no(cleaned)
        if intent == "yes":
            return "Yes"
        if intent == "no":
            return "No"

    return cleaned


def _should_confirm_followup_answer(question: str, raw_answer: str, normalized_answer: str) -> bool:
    question_lower = question.lower()
    raw_clean = _clean_spoken_text(raw_answer).lower()
    normalized_clean = _clean_spoken_text(normalized_answer).lower()

    if "qualification" in question_lower or "education" in question_lower:
        return True
    if "percentage" in question_lower or "score" in question_lower or "marks" in question_lower:
        return True
    if raw_clean != normalized_clean:
        return True

    return False


def _prepare_query_text(text: str) -> str | None:
    cleaned = _clean_spoken_text(text)
    cleaned = re.sub(r"^(just say|just tell me|tell me|please tell me|can you tell me)\s+", "", cleaned, flags=re.I)
    cleaned = cleaned.strip(" .?!,")

    if not cleaned or _looks_like_garbled_text(cleaned):
        return None

    if cleaned.lower().endswith((" the", " a", " an", " into", " in the", " on the", " of the", " for the")):
        return None

    vague_tokens = {"them", "that", "this", "there"}
    tokens = re.findall(r"[a-zA-Z]+", cleaned.lower())
    if tokens and len(tokens) <= 6 and sum(token in vague_tokens for token in tokens) >= 2:
        return None

    return cleaned


def _truncate_to_two_sentences(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    if not parts:
        return text.strip()
    return " ".join(part for part in parts[:2] if part).strip()


def _sanitize_voice_answer(answer: str) -> str:
    cleaned = _clean_spoken_text(answer)
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    cleaned = re.sub(r"\(Source:.*?\)", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -")

    if not cleaned or _looks_like_garbled_text(cleaned):
        return VOICE_QUERY_FALLBACK

    cleaned = _truncate_to_two_sentences(cleaned)
    if len(cleaned) > 260:
        cleaned = cleaned[:257].rstrip(",;: ") + "."

    return cleaned or VOICE_QUERY_FALLBACK


def normalize_outbound_phone(raw_phone: str, default_country_code: str = VOICE_DEFAULT_COUNTRY_CODE) -> str:
    """
    Convert raw phone values into E.164-ish output.
    - 10 digits -> default country code (e.g., +91XXXXXXXXXX)
    - already prefixed with + and digits -> passthrough
    - otherwise digits-only passthrough (for already complete country code without +)
    """
    phone = (raw_phone or "").strip()
    if not phone:
        raise ValueError("Phone number is empty")

    if phone.startswith("+"):
        digits = re.sub(r"[^0-9]", "", phone)
        if len(digits) < 10:
            raise ValueError("Invalid phone number")
        return f"+{digits}"

    digits = re.sub(r"[^0-9]", "", phone)
    if len(digits) == 10:
        cc_digits = re.sub(r"[^0-9]", "", default_country_code or "91")
        return f"+{cc_digits}{digits}"
    if len(digits) >= 11:
        return f"+{digits}"

    raise ValueError("Invalid phone number")


def _to_ws_base_url(public_base_url: str) -> str:
    parsed = urlparse(public_base_url.rstrip("/"))
    if parsed.scheme == "https":
        scheme = "wss"
    elif parsed.scheme == "http":
        scheme = "ws"
    else:
        raise ValueError("VOICE_PUBLIC_BASE_URL must start with http:// or https://")
    return urlunparse((scheme, parsed.netloc, "", "", "", ""))


def build_voice_webhook_url(session_id: str) -> str:
    base = _get_voice_public_base_url()
    if not base:
        raise ValueError("VOICE_PUBLIC_BASE_URL is not configured")
    return f"{base}/voice?session_id={quote(session_id)}"


def build_stream_ws_url(session_id: str) -> str:
    base = _get_voice_public_base_url()
    if not base:
        raise ValueError("VOICE_PUBLIC_BASE_URL is not configured")
    ws_base = _to_ws_base_url(base)
    return f"{ws_base}/ws?session_id={quote(session_id)}"


def build_voice_twiml(session_id: str) -> str:
    stream_url = escape(build_stream_ws_url(session_id))
    session_value = escape(session_id)
    return (
        "<Response>\n"
        "  <Connect>\n"
        f"    <Stream url=\"{stream_url}\">\n"
        f"      <Parameter name=\"session_id\" value=\"{session_value}\" />\n"
        "    </Stream>\n"
        "  </Connect>\n"
        "</Response>\n"
    )


def _get_twilio_client() -> Any:
    try:
        from twilio.rest import Client
    except ModuleNotFoundError as exc:
        raise RuntimeError("twilio package is missing. Run `pip install -r requirements.txt`.") from exc

    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        raise ValueError("TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN must be set")
    return Client(sid, token)


def get_twilio_number() -> str:
    number = (os.getenv("TWILIO_NUMBER") or "").strip()
    if not number:
        raise ValueError("TWILIO_NUMBER must be set")
    return number


def initiate_outbound_call(session_id: str, raw_phone: str) -> dict:
    """Trigger outbound Twilio call and mark lead status as `calling`."""
    existing_lead = load_lead(session_id)
    if existing_lead:
        current_status = str(existing_lead.get("voicebot_status") or "").strip().lower()
        if current_status in {"calling", "in_progress", "completed"}:
            return {"status": "skipped", "reason": f"voicebot already {current_status}"}

    to_number = normalize_outbound_phone(raw_phone)
    voice_url = build_voice_webhook_url(session_id)
    client = _get_twilio_client()

    call = client.calls.create(
        to=to_number,
        from_=get_twilio_number(),
        url=voice_url,
    )

    update_voicebot_status(
        session_id,
        "calling",
        {"call_sid": call.sid, "to": to_number, "voice_url": voice_url, "updated_at": datetime.now().isoformat()},
    )

    return {"call_sid": call.sid, "to": to_number, "voice_url": voice_url}


def initiate_outbound_call_safe(session_id: str, raw_phone: str) -> dict:
    """Safe wrapper used by background tasks."""
    try:
        return initiate_outbound_call(session_id, raw_phone)
    except Exception as exc:
        mark_voicebot_status(
            session_id,
            "failed",
            {"error": str(exc), "updated_at": datetime.now().isoformat()},
        )
        return {"error": str(exc)}


def hangup_call(call_sid: str) -> None:
    if not call_sid:
        return
    try:
        client = _get_twilio_client()
        client.calls(call_sid).update(status="completed")
    except Exception:
        # Best effort; avoid crashing websocket cleanup.
        pass


def parse_yes_no(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return "unknown"

    tokens = set(normalized.split())

    if tokens & YES_WORDS:
        return "yes"
    if tokens & NO_WORDS:
        return "no"

    if normalized.startswith("yes"):
        return "yes"
    if normalized.startswith("no"):
        return "no"

    return "unknown"


@dataclass
class ConversationStep:
    reply: str = ""
    should_end: bool = False
    needs_query_answer: bool = False
    query_text: str = ""


@dataclass
class VoiceConversationState:
    session_id: str
    lead: dict[str, Any]
    call_sid: str = ""
    stream_sid: str = ""
    followup_questions: list[str] = field(default_factory=list)
    followup_answers: list[dict[str, str]] = field(default_factory=list)
    query_turns: list[dict[str, str]] = field(default_factory=list)
    question_index: int = 0
    pending_followup_question: str = ""
    pending_followup_answer: str = ""
    mode: str = "INIT"
    completed: bool = False

    @classmethod
    def from_session_id(cls, session_id: str, call_sid: str = "", stream_sid: str = "") -> "VoiceConversationState":
        lead = load_lead(session_id)
        if not lead:
            raise ValueError(f"Lead not found for session_id={session_id}")

        questions = [
            str(lead.get("followup_q1") or "").strip(),
            str(lead.get("followup_q2") or "").strip(),
            str(lead.get("followup_q3") or "").strip(),
            str(lead.get("followup_q4") or "").strip(),
            str(lead.get("followup_q5") or "").strip(),
        ]
        questions = [q for q in questions if q]
        return cls(
            session_id=session_id,
            lead=lead,
            call_sid=call_sid,
            stream_sid=stream_sid,
            followup_questions=questions,
        )

    def opening_prompt(self) -> str:
        course = str(self.lead.get("course_of_interest") or "").strip()
        if course:
            greeting = (
                f"Hello, this is the Sathyabama admissions assistant calling regarding your {course} enquiry."
            )
        else:
            greeting = "Hello, this is the Sathyabama admissions assistant. Thank you for your enquiry."

        if self.followup_questions:
            self.mode = "ASK_FOLLOWUPS"
            question = self.followup_questions[0]
            return f"{greeting} I have a few brief follow up questions. First question. {question}"

        self.mode = "ANY_QUERY_CONFIRM"
        return f"{greeting} I do not have additional follow up questions. Do you have any query? Please say yes or no."

    def handle_transcript(self, transcript: str) -> ConversationStep:
        text = (transcript or "").strip()
        if not text:
            return ConversationStep(reply="Sorry, I could not hear you clearly. Please repeat.")

        if self.mode == "ASK_FOLLOWUPS":
            question = self.followup_questions[self.question_index]
            normalized_answer = _normalize_followup_answer(question, text)
            if not normalized_answer:
                return ConversationStep(reply=f"{VOICE_REPEAT_FOLLOWUP} {question}")

            if _should_confirm_followup_answer(question, text, normalized_answer):
                self.pending_followup_question = question
                self.pending_followup_answer = normalized_answer
                self.mode = "CONFIRM_FOLLOWUP_ANSWER"
                return ConversationStep(
                    reply=f"I heard {normalized_answer}. Is that correct? Please say yes or no."
                )

            self.followup_answers.append({"question": question, "answer": normalized_answer})
            self.question_index += 1

            if self.question_index < len(self.followup_questions):
                return ConversationStep(reply=f"Thank you. Next question. {self.followup_questions[self.question_index]}")

            self.mode = "ANY_QUERY_CONFIRM"
            return ConversationStep(reply="Thank you for your responses. Do you have any question? Please say yes or no.")

        if self.mode == "CONFIRM_FOLLOWUP_ANSWER":
            intent = parse_yes_no(text)
            if intent == "yes":
                self.followup_answers.append(
                    {"question": self.pending_followup_question, "answer": self.pending_followup_answer}
                )
                self.pending_followup_question = ""
                self.pending_followup_answer = ""
                self.question_index += 1

                if self.question_index < len(self.followup_questions):
                    self.mode = "ASK_FOLLOWUPS"
                    return ConversationStep(
                        reply=f"Thank you. Next question. {self.followup_questions[self.question_index]}"
                    )

                self.mode = "ANY_QUERY_CONFIRM"
                return ConversationStep(
                    reply="Thank you for your responses. Do you have any question? Please say yes or no."
                )

            if intent == "no":
                question = self.pending_followup_question or self.followup_questions[self.question_index]
                self.pending_followup_question = ""
                self.pending_followup_answer = ""
                self.mode = "ASK_FOLLOWUPS"
                return ConversationStep(reply=f"Okay. Please answer again. {question}")

            return ConversationStep(reply="Please say yes or no.")

        if self.mode in {"ANY_QUERY_CONFIRM", "MORE_QUERY_CONFIRM"}:
            intent = parse_yes_no(text)
            if intent == "yes":
                self.mode = "QUERY_TEXT"
                return ConversationStep(reply="Please ask your question in one short sentence.")
            if intent == "no":
                self.mode = "COMPLETED"
                self.completed = True
                return ConversationStep(
                    reply="Thank you for your time. Our admissions team will reach out soon. Goodbye.",
                    should_end=True,
                )
            return ConversationStep(reply="Please say yes or no.")

        if self.mode == "QUERY_TEXT":
            query_text = _prepare_query_text(text)
            if not query_text:
                return ConversationStep(reply=VOICE_REPEAT_QUERY)
            return ConversationStep(needs_query_answer=True, query_text=query_text)

        return ConversationStep(reply="Thank you. Goodbye.", should_end=True)

    def register_query_answer(self, query: str, answer: str) -> str:
        self.query_turns.append({"query": query, "answer": answer})
        self.mode = "MORE_QUERY_CONFIRM"
        return f"{answer} Do you have any other query? Please say yes or no."

    def status_payload(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "call_sid": self.call_sid,
            "stream_sid": self.stream_sid,
            "followup_qa": self.followup_answers,
            "query_turns": self.query_turns,
            "mode": self.mode,
            "completed": self.completed,
            "updated_at": datetime.now().isoformat(),
        }


def answer_query_with_qdrant(query_text: str) -> str:
    try:
        chunks = retrieve(query_text, top_k=4, backend_override="qdrant")
        if not chunks:
            return VOICE_QUERY_FALLBACK

        answer = generate(
            query_text,
            chunks,
            system_prompt=VOICE_QUERY_SYSTEM_PROMPT,
            max_tokens=180,
            temperature=0.1,
        )
        return _sanitize_voice_answer(answer)
    except Exception as exc:
        print(f"[voicebot] Query answer failed: {exc}")
        return VOICE_QUERY_FALLBACK


def mark_voicebot_status(session_id: str, status: str, payload: dict[str, Any] | None = None) -> None:
    update_voicebot_status(session_id, status, payload or {})
