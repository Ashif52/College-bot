import asyncio
import base64
import json
import os

import httpx
import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from chatbot.api import router as chatbot_router
from chatbot.excel_store import load_lead
from chatbot.voicebot_service import (
    VoiceConversationState,
    answer_query_with_qdrant,
    build_voice_twiml,
    hangup_call,
    initiate_outbound_call,
    mark_voicebot_status,
)

load_dotenv()

DEEPGRAM_KEY = os.getenv("DEEPGRAM_API_KEY")

DG_STREAM_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?model=nova-3"
    "&encoding=mulaw"
    "&sample_rate=8000"
    "&smart_format=true"
    "&punctuate=true"
    "&endpointing=300"
    "&interim_results=false"
)

# Send TTS audio in 640-byte chunks (80ms of mulaw @ 8000Hz)
TTS_CHUNK_BYTES = 640

app = FastAPI(title="Sathyabama AI Platform")

# Mount the RAG chatbot under /chatbot
app.include_router(chatbot_router, prefix="/chatbot")

# Serve the chat UI static files at /chatbot/static/
app.mount("/chatbot/static", StaticFiles(directory="chatbot/static"), name="chatbot_static")


@app.get("/", include_in_schema=False)
def root():
    """Redirect root to the chat UI."""
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

    async def deepgram_receiver(dg_ws):
        async for raw in dg_ws:
            try:
                msg = json.loads(raw)
                alt = msg.get("channel", {}).get("alternatives", [{}])[0]
                transcript = alt.get("transcript", "").strip()
                is_final = msg.get("speech_final", False)

                if transcript and is_final:
                    print("USER:", transcript)
                    async with process_lock:
                        await handle_transcript(transcript)
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
