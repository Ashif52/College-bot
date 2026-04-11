# chatbot/session.py
# ─────────────────────────────────────────────────────────────────────────────
# Session manager for the college admission chatbot.
# Implements a state-machine flow:
#   GREETING → AWAIT_FIRST_MSG → COLLECT_NAME → COLLECT_PHONE → ANSWERING → ENDED
# ─────────────────────────────────────────────────────────────────────────────

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from chatbot import pipeline as rag_pipeline
from chatbot.faq import lookup_faq_answer
from chatbot.public_text import COLLEGE_NAME


class ChatState(str, Enum):
    GREETING       = "GREETING"
    AWAIT_FIRST_MSG = "AWAIT_FIRST_MSG"   # session created, waiting for first user message
    COLLECT_NAME   = "COLLECT_NAME"        # first msg stored, asking for name
    COLLECT_PHONE  = "COLLECT_PHONE"       # name stored, asking for phone
    ANSWERING      = "ANSWERING"           # lead captured, answering questions
    ENDED          = "ENDED"               # session closed, data saved


@dataclass
class Message:
    role: str           # "user" | "bot"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ChatSession:
    session_id: str       = field(default_factory=lambda: str(uuid.uuid4()))
    state: ChatState      = ChatState.GREETING
    student_name: str     = ""
    phone_number: str     = ""
    first_query: str      = ""
    history: list[Message] = field(default_factory=list)
    started_at: str       = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: str         = ""

    # AI-generated data (filled at session end)
    chat_summary: str          = ""
    course_of_interest: str    = ""
    current_education: str     = ""
    location: str              = ""
    followup_questions: list[str] = field(default_factory=list)


# ── In-memory session store ────────────────────────────────────────────────────
_sessions: dict[str, ChatSession] = {}


def create_session() -> ChatSession:
    """Create a new chat session and return the greeting message."""
    session = ChatSession()
    _sessions[session.session_id] = session

    greeting = (
        f"👋 Hello! Welcome to **{COLLEGE_NAME}**!\n\n"
        "I'm your virtual admissions assistant. I'm here to help you with any questions "
        "about courses, eligibility, fees, hostel facilities, and more.\n\n"
        "How can I help you today? Feel free to ask anything! 😊"
    )
    session.history.append(Message(role="bot", content=greeting))
    session.state = ChatState.AWAIT_FIRST_MSG
    return session


def get_session(session_id: str) -> Optional[ChatSession]:
    """Retrieve an existing session by ID."""
    return _sessions.get(session_id)


def _validate_phone(text: str) -> bool:
    """Basic phone number validation — at least 10 digits."""
    digits = re.sub(r"[^0-9]", "", text)
    return len(digits) >= 10


def _normalize_phone(text: str) -> str:
    """Strip formatting and return a clean phone number."""
    digits = re.sub(r"[^0-9+]", "", text)
    return digits


def process_message(session_id: str, user_text: str) -> dict:
    """
    Main entry point: given a user message, advance the state machine
    and return { "reply": str, "state": str, "session_ended": bool }.
    """
    session = _sessions.get(session_id)
    if not session:
        return {"reply": "Session not found. Please refresh the page.", "state": "ERROR", "session_ended": False}

    if session.state == ChatState.ENDED:
        return {"reply": "This chat session has already ended. Please refresh to start a new one.",
                "state": "ENDED", "session_ended": True}

    # Record user message
    session.history.append(Message(role="user", content=user_text))

    # ── State transitions ──────────────────────────────────────────────────────
    if session.state == ChatState.AWAIT_FIRST_MSG:
        # Store first question, ask for name
        session.first_query = user_text
        session.state = ChatState.COLLECT_NAME
        reply = (
            "That's a great question! 🌟\n\n"
            "Before I answer, may I know your **name** please? "
            "This helps me personalise our conversation for you."
        )

    elif session.state == ChatState.COLLECT_NAME:
        # Store name, ask for phone
        session.student_name = user_text.strip().title()
        session.state = ChatState.COLLECT_PHONE
        reply = (
            f"Wonderful, **{session.student_name}**! 😊\n\n"
            "Could you also share your **phone number**? "
            "Our admissions team may reach out to assist you further."
        )

    elif session.state == ChatState.COLLECT_PHONE:
        # Validate phone
        if not _validate_phone(user_text):
            reply = (
                "Hmm, that doesn't look like a valid phone number. "
                "Please enter at least a 10-digit phone number (e.g. 9876543210)."
            )
        else:
            session.phone_number = _normalize_phone(user_text)
            session.state = ChatState.ANSWERING

            # Now answer the original question
            answer = _get_rag_answer(session.first_query)
            reply = (
                f"Thank you, **{session.student_name}**! 🎉 "
                "I'll now answer your earlier question:\n\n"
                f"{answer}\n\n"
                "Feel free to ask more questions!"
            )
            session.history.append(Message(role="bot", content=reply))
            return {"reply": reply, "state": session.state.value, "session_ended": False}

    elif session.state == ChatState.ANSWERING:
        # Regular Q&A via RAG
        answer = _get_rag_answer(user_text)
        reply = answer

    else:
        reply = "I'm not sure how to help with that right now. Please try again."

    session.history.append(Message(role="bot", content=reply))
    return {"reply": reply, "state": session.state.value, "session_ended": False}


def _get_rag_answer(question: str) -> str:
    """Call the RAG pipeline and return the answer string."""
    try:
        _, fast_answer = lookup_faq_answer(question)
        if fast_answer:
            return fast_answer
        result = rag_pipeline.query(question)
        return result.answer
    except Exception:
        return "I'm having trouble searching the knowledge base right now. Please try again or contact admissions."


def end_session(session_id: str) -> ChatSession:
    """
    End the session: mark as ENDED, trigger AI summary + follow-up question generation.
    Returns the finalised session object (caller should then save to Excel).
    """
    session = _sessions.get(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    if session.state == ChatState.ENDED:
        return session

    session.state = ChatState.ENDED
    session.ended_at = datetime.now().isoformat()

    # Only generate AI analysis if we got past the lead-capture stage
    if session.student_name:
        try:
            from chatbot.question_generator import generate_followup_data
            result = generate_followup_data(session)
            session.chat_summary      = result.get("chat_summary", "")
            session.course_of_interest = result.get("course_of_interest", "")
            session.current_education  = result.get("current_education", "")
            session.location           = result.get("location", "")
            session.followup_questions = result.get("followup_questions", [])
        except Exception as e:
            print(f"[session] Warning: follow-up generation failed: {e}")

    return session
