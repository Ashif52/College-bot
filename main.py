from __future__ import annotations

import asyncio
import base64
import json
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from chatbot.api import router as chatbot_router
from chatbot.excel_store import load_lead
from chatbot.faq import preload_faq_data
from chatbot.retriever import prewarm_embedder_and_qdrant
from chatbot.voicebot_service import (
    VoiceConversationState,
    VOICE_QUERY_FILLER,
    answer_query_with_qdrant,
    build_voice_twiml,
    get_fast_path_answer,
    hangup_call,
    initiate_outbound_call,
    mark_voicebot_status,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"

DEEPGRAM_KEY = os.getenv("DEEPGRAM_API_KEY")
DG_ENDPOINTING_MS = int(os.getenv("DG_ENDPOINTING_MS", "220"))
VOICE_QUERY_BUFFER_FLUSH_SECONDS = float(os.getenv("VOICE_QUERY_BUFFER_FLUSH_SECONDS", "0.45"))

DG_STREAM_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?model=nova-3"
    "&encoding=mulaw"
    "&sample_rate=8000"
    "&smart_format=true"
    "&punctuate=true"
    f"&endpointing={DG_ENDPOINTING_MS}"
    "&interim_results=false"
)

# Send TTS audio in 640-byte chunks (80ms of mulaw @ 8000Hz)
TTS_CHUNK_BYTES = 640


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fire-and-forget prewarm so the app starts accepting HTTP immediately.
    # Railway kills the container if it doesn't respond within the health-check
    # window (~60 s), and the ML-model download can take longer than that.
    async def _background_prewarm():
        try:
            await asyncio.to_thread(prewarm_embedder_and_qdrant)
            await asyncio.to_thread(preload_faq_data)
            print("[startup] Prewarm complete")
        except Exception as exc:
            print(f"[startup] Prewarm skipped: {exc}")

    asyncio.create_task(_background_prewarm())
    yield


app = FastAPI(title="Nexus AI Platform", lifespan=lifespan)

# Mount the RAG chatbot under /chatbot
app.include_router(chatbot_router, prefix="/chatbot")

# Serve the chat UI static files at /chatbot/static/
app.mount("/chatbot/static", StaticFiles(directory="chatbot/static"), name="chatbot_static")



@app.get("/health")
def root_health():
    """Top-level health check for Railway / load-balancer probes."""
    return {"status": "ok"}




@app.get("/legacy-chat", include_in_schema=False)
def legacy_chat():
    """Keep the legacy standalone chat UI available for manual testing."""
    return RedirectResponse(url="/chatbot/static/chat.html")


@app.api_route("/voice", methods=["GET", "POST"])
def voice(session_id: str = ""):
    session_id = (session_id or "").strip()
    if not session_id:
        twiml = (
            "<Response>"
            "<Say>Sorry, we could not locate your session. Please contact admissions office.</Say>"
            "<Hangup/>"
            "</Response>"
        )
        return Response(content=twiml, media_type="application/xml")

    twiml = build_voice_twiml(session_id)
    return Response(content=twiml, media_type="application/xml")


@app.get("/make-call/{session_id}")
def make_call(session_id: str):
    lead = load_lead(session_id)
    if not lead:
        return {"status": "error", "message": f"Lead not found for session_id={session_id}"}

    phone_number = str(lead.get("phone_number") or "").strip()
    if not phone_number:
        return {"status": "error", "message": "Lead has no phone number"}

    result = initiate_outbound_call(session_id, phone_number)
    return {"status": "calling", **result}


@app.get("/make-call")
def make_call_legacy(session_id: str = "", phone_number: str = ""):
    """Backward-compatible manual trigger endpoint."""
    session_id = (session_id or "").strip()
    phone_number = (phone_number or "").strip()

    if not session_id and not phone_number:
        return {
            "status": "error",
            "message": "Provide session_id (preferred) or both session_id and phone_number.",
        }

    if session_id and not phone_number:
        return make_call(session_id)

    if not session_id:
        return {"status": "error", "message": "session_id is required when using phone_number override."}

    result = initiate_outbound_call(session_id, phone_number)
    return {"status": "calling", **result}


async def stream_tts_to_twilio(text: str, twilio_ws: WebSocket, stream_sid: str):
    """Stream TTS audio to Twilio chunk-by-chunk as it arrives from Deepgram."""
    url = (
        "https://api.deepgram.com/v1/speak"
        "?model=aura-asteria-en&encoding=mulaw&sample_rate=8000&container=none"
    )
    headers = {
        "Authorization": f"Token {DEEPGRAM_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream("POST", url, headers=headers, json={"text": text}) as resp:
            buffer = b""
            async for raw_chunk in resp.aiter_bytes():
                buffer += raw_chunk
                while len(buffer) >= TTS_CHUNK_BYTES:
                    piece = buffer[:TTS_CHUNK_BYTES]
                    buffer = buffer[TTS_CHUNK_BYTES:]
                    await twilio_ws.send_json(
                        {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": base64.b64encode(piece).decode()},
                        }
                    )

            if buffer:
                await twilio_ws.send_json(
                    {
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": base64.b64encode(buffer).decode()},
                    }
                )

    await twilio_ws.send_json(
        {
            "event": "mark",
            "streamSid": stream_sid,
            "mark": {"name": "done"},
        }
    )


@app.websocket("/ws")
async def websocket_endpoint(twilio_ws: WebSocket):
    await twilio_ws.accept()
    print("Twilio connected")

    session_id = (twilio_ws.query_params.get("session_id") or "").strip()
    stream_sid = ""
    call_sid = ""
    conversation: VoiceConversationState | None = None
    status_committed = False
    audio_queue: asyncio.Queue[bytes | None] = asyncio.Queue()
    process_lock = asyncio.Lock()
    latest_final_transcript = ""
    last_processed_transcript = ""
    last_processed_at = 0.0
    buffered_transcript = ""
    buffered_flush_task: asyncio.Task | None = None

    async def commit_status(status: str, extra: dict | None = None):
        nonlocal status_committed
        if not session_id:
            return
        payload = {}
        if conversation:
            payload.update(conversation.status_payload())
        if extra:
            payload.update(extra)
        mark_voicebot_status(session_id, status, payload)
        if status in {"completed", "failed"}:
            status_committed = True

    async def speak(text: str):
        if stream_sid and text:
            await stream_tts_to_twilio(text, twilio_ws, stream_sid)

    async def deepgram_sender(dg_ws):
        while True:
            chunk = await audio_queue.get()
            if chunk is None:
                break
            try:
                await dg_ws.send(chunk)
            except Exception:
                break

    async def handle_transcript(transcript: str):
        if not conversation:
            return

        step = conversation.handle_transcript(transcript)

        if step.needs_query_answer:
            fast_answer = get_fast_path_answer(step.query_text)
            if fast_answer:
                reply = conversation.register_query_answer(step.query_text, fast_answer)
                await speak(reply)
                return

            await speak(VOICE_QUERY_FILLER)
            answer = await asyncio.to_thread(answer_query_with_qdrant, step.query_text)
            reply = conversation.register_query_answer(step.query_text, answer)
            await speak(reply)
            return

        if step.reply:
            await speak(step.reply)

        if step.should_end:
            await commit_status("completed")
            await asyncio.sleep(0.8)
            await asyncio.to_thread(hangup_call, conversation.call_sid)

    async def process_final_transcript(transcript: str, source: str):
        nonlocal last_processed_transcript, last_processed_at
        cleaned = (transcript or "").strip()
        if not cleaned:
            return

        now = asyncio.get_running_loop().time()
        if cleaned == last_processed_transcript and (now - last_processed_at) < 1.5:
            return

        print(f"USER ({source}):", cleaned)
        last_processed_transcript = cleaned
        last_processed_at = now
        async with process_lock:
            await handle_transcript(cleaned)

    def should_buffer_current_mode() -> bool:
        if not conversation:
            return False
        return conversation.mode in {"ANY_QUERY_CONFIRM", "MORE_QUERY_CONFIRM", "QUERY_TEXT"}

    def merge_transcripts(existing: str, new_text: str) -> str:
        existing = (existing or "").strip()
        new_text = (new_text or "").strip()
        if not existing:
            return new_text
        if not new_text:
            return existing

        existing_norm = re.sub(r"\s+", " ", existing).lower()
        new_norm = re.sub(r"\s+", " ", new_text).lower()
        if new_norm in existing_norm:
            return existing
        if existing_norm in new_norm:
            return new_text

        existing_words = existing.split()
        new_words = new_text.split()
        max_overlap = min(len(existing_words), len(new_words), 6)
        for overlap in range(max_overlap, 0, -1):
            existing_tail = [word.lower() for word in existing_words[-overlap:]]
            new_head = [word.lower() for word in new_words[:overlap]]
            if existing_tail == new_head:
                return " ".join(existing_words + new_words[overlap:])

        return f"{existing} {new_text}".strip()

    def cancel_buffered_flush() -> None:
        nonlocal buffered_flush_task
        if buffered_flush_task and not buffered_flush_task.done():
            buffered_flush_task.cancel()
        buffered_flush_task = None

    async def flush_buffered_transcript(source: str):
        nonlocal buffered_transcript
        transcript = buffered_transcript.strip()
        buffered_transcript = ""
        if transcript:
            await process_final_transcript(transcript, source)

    async def schedule_buffered_flush():
        try:
            await asyncio.sleep(VOICE_QUERY_BUFFER_FLUSH_SECONDS)
            await flush_buffered_transcript("buffer_timeout")
        except asyncio.CancelledError:
            pass

    async def deepgram_receiver(dg_ws):
        nonlocal latest_final_transcript, buffered_transcript, buffered_flush_task
        async for raw in dg_ws:
            try:
                msg = json.loads(raw)
                alt = msg.get("channel", {}).get("alternatives", [{}])[0]
                transcript = alt.get("transcript", "").strip()
                is_final = msg.get("is_final", False)
                speech_final = msg.get("speech_final", False)

                if transcript and is_final:
                    latest_final_transcript = transcript

                if transcript and is_final and should_buffer_current_mode():
                    buffered_transcript = merge_transcripts(buffered_transcript, transcript)
                    if speech_final:
                        cancel_buffered_flush()
                        await flush_buffered_transcript("speech_final_buffered")
                    else:
                        cancel_buffered_flush()
                        buffered_flush_task = asyncio.create_task(schedule_buffered_flush())
                    latest_final_transcript = ""
                    continue

                if speech_final and latest_final_transcript:
                    await process_final_transcript(latest_final_transcript, "speech_final")
                    latest_final_transcript = ""
                    continue

                # On phone audio, Deepgram may emit a clean final segment without
                # a later speech_final. Short follow-up answers and short questions
                # should still move the conversation forward.
                if transcript and is_final:
                    await process_final_transcript(transcript, "is_final")
                    latest_final_transcript = ""
            except Exception as exc:
                print("DG RECV ERROR:", exc)

    try:
        async with websockets.connect(
            DG_STREAM_URL,
            additional_headers={"Authorization": f"Token {DEEPGRAM_KEY}"},
            ping_interval=10,
        ) as dg_ws:
            print("Deepgram connected")

            dg_tasks = asyncio.gather(
                deepgram_sender(dg_ws),
                deepgram_receiver(dg_ws),
            )

            try:
                while True:
                    raw = await twilio_ws.receive_text()
                    msg = json.loads(raw)
                    event = msg.get("event")

                    if event == "start":
                        start_data = msg.get("start", {})
                        stream_sid = start_data.get("streamSid", "")
                        call_sid = start_data.get("callSid", "")
                        print(f"Stream started: {stream_sid}")

                        if not session_id:
                            custom = start_data.get("customParameters", {})
                            session_id = str(custom.get("session_id", "")).strip()

                        if not session_id:
                            await speak("Sorry, session details are missing. Ending this call now.")
                            if call_sid:
                                await asyncio.to_thread(hangup_call, call_sid)
                            break

                        try:
                            conversation = VoiceConversationState.from_session_id(
                                session_id=session_id,
                                call_sid=call_sid,
                                stream_sid=stream_sid,
                            )
                            opening_prompt = conversation.opening_prompt()
                            await commit_status("in_progress")
                            await speak(opening_prompt)
                        except Exception as exc:
                            await commit_status("failed", {"error": str(exc)})
                            await speak(
                                "Sorry, we could not load your enquiry details right now. "
                                "Please contact admissions office."
                            )
                            if call_sid:
                                await asyncio.to_thread(hangup_call, call_sid)
                            break

                    elif event == "media":
                        payload = msg.get("media", {}).get("payload")
                        if payload:
                            await audio_queue.put(base64.b64decode(payload))

                    elif event == "stop":
                        print("Stream stopped")
                        break

            finally:
                await audio_queue.put(None)
                cancel_buffered_flush()
                dg_tasks.cancel()
                try:
                    await dg_tasks
                except asyncio.CancelledError:
                    pass

    except Exception as exc:
        print("WEBSOCKET FLOW ERROR:", exc)
        if conversation and session_id:
            await commit_status("failed", {"error": str(exc)})

    finally:
        if conversation and session_id and not status_committed:
            status = "completed" if conversation.completed else "failed"
            await commit_status(status)


if FRONTEND_DIST_DIR.exists():
    # Mount the production frontend after API and websocket routes so those
    # endpoints keep working while the website is served from the same app.
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")
