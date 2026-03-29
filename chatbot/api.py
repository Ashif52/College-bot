# chatbot/api.py
# ─────────────────────────────────────────────────────────────────────────────
# FastAPI router for the RAG chatbot + session-based lead capture chatbot.
# Mount this into main.py with:
#   from chatbot.api import router as chatbot_router
#   app.include_router(chatbot_router, prefix="/chatbot")
# ─────────────────────────────────────────────────────────────────────────────

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from chatbot import pipeline
from chatbot.config import LLM_PROVIDER, GROQ_MODEL, OPENAI_MODEL
from chatbot import session as session_mgr
from chatbot.excel_store import save_lead

router = APIRouter(tags=["Chatbot"])


# ── Request / Response models ──────────────────────────────────────────────────

# Legacy single-shot RAG chat
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, example="What is the MCA eligibility?")
    top_k:    int = Field(5, ge=1, le=10, description="Number of chunks to retrieve")

class ChatResponse(BaseModel):
    question: str
    answer:   str
    sources:  list[str]
    provider: str
    model:    str

# Session-based chat
class SessionStartResponse(BaseModel):
    session_id: str
    greeting:   str
    state:      str

class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, example="I want to know about MBA admissions")

class MessageResponse(BaseModel):
    reply:          str
    state:          str
    session_ended:  bool

class SessionEndResponse(BaseModel):
    session_id:          str
    student_name:        str
    phone_number:        str
    chat_summary:        str
    course_of_interest:  str
    followup_questions:  list[str]
    excel_saved:         bool


# ── Endpoints ─────────────────────────────────────────────────────────────────

# ── Legacy RAG endpoint (unchanged) ───────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse, summary="Ask the Sathyabama chatbot (single-shot RAG)")
def chat(req: ChatRequest) -> ChatResponse:
    """Ask any question about Sathyabama Institute (no lead capture)."""
    try:
        result = pipeline.query(req.question, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {e}")

    model_name = GROQ_MODEL if LLM_PROVIDER == "groq" else OPENAI_MODEL
    return ChatResponse(
        question=result.question,
        answer=result.answer,
        sources=result.sources,
        provider=LLM_PROVIDER,
        model=model_name,
    )


# ── Session: Start ─────────────────────────────────────────────────────────────
@router.post(
    "/session/start",
    response_model=SessionStartResponse,
    summary="Start a new chatbot session"
)
def start_session() -> SessionStartResponse:
    """Create a new chat session. Returns session_id and the opening greeting."""
    sess = session_mgr.create_session()
    greeting = sess.history[0].content if sess.history else ""
    return SessionStartResponse(
        session_id=sess.session_id,
        greeting=greeting,
        state=sess.state.value,
    )


# ── Session: Send Message ──────────────────────────────────────────────────────
@router.post(
    "/session/{session_id}/message",
    response_model=MessageResponse,
    summary="Send a message in an existing session"
)
def send_message(session_id: str, req: MessageRequest) -> MessageResponse:
    """Process a user message and return the bot reply."""
    result = session_mgr.process_message(session_id, req.message)
    return MessageResponse(
        reply=result["reply"],
        state=result["state"],
        session_ended=result["session_ended"],
    )


# ── Session: End ───────────────────────────────────────────────────────────────
@router.post(
    "/session/{session_id}/end",
    response_model=SessionEndResponse,
    summary="End a session, generate follow-up questions, and save to Excel"
)
def end_session(session_id: str) -> SessionEndResponse:
    """
    End the chat session:
    1. Generate AI summary + follow-up questions
    2. Save lead data to leads.xlsx
    3. Return final session data
    """
    try:
        sess = session_mgr.end_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    excel_saved = False
    if sess.student_name:
        try:
            save_lead(sess)
            excel_saved = True
        except Exception as e:
            print(f"[api] Excel save failed: {e}")

    return SessionEndResponse(
        session_id=sess.session_id,
        student_name=sess.student_name,
        phone_number=sess.phone_number,
        chat_summary=sess.chat_summary,
        course_of_interest=sess.course_of_interest,
        followup_questions=sess.followup_questions,
        excel_saved=excel_saved,
    )


# ── Session: Status ────────────────────────────────────────────────────────────
@router.get(
    "/session/{session_id}/status",
    summary="Get the current state of a session"
)
def session_status(session_id: str) -> dict:
    """Check state, name, and turn count for an existing session."""
    sess = session_mgr.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return {
        "session_id":   sess.session_id,
        "state":        sess.state.value,
        "student_name": sess.student_name,
        "phone_number": sess.phone_number,
        "turns":        len([m for m in sess.history if m.role == "user"]),
    }


# ── Health ─────────────────────────────────────────────────────────────────────
@router.get("/health", summary="Chatbot health check")
def health() -> dict:
    return {
        "status":   "ok",
        "provider": LLM_PROVIDER,
        "model":    GROQ_MODEL if LLM_PROVIDER == "groq" else OPENAI_MODEL,
    }
