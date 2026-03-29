import asyncio
import base64
import json
import os

import httpx
import websockets
from fastapi import FastAPI, WebSocket
from fastapi.responses import Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from twilio.rest import Client
from groq import Groq
from dotenv import load_dotenv

# ── Chatbot RAG router ─────────────────────────────────────────────────────────
from chatbot.api import router as chatbot_router

load_dotenv()

TWILIO_SID    = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
DEEPGRAM_KEY  = os.getenv("DEEPGRAM_API_KEY")
GROQ_KEY      = os.getenv("GROQ_API_KEY")

twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
groq_client   = Groq(api_key=GROQ_KEY)

DG_STREAM_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?model=nova-3"
    "&encoding=mulaw"
    "&sample_rate=8000"
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


@app.post("/voice")
def voice():
    twiml = """
<Response>
    <Connect>
        <Stream url="wss://abactinal-laura-unowned.ngrok-free.dev/ws"/>
    </Connect>
</Response>
"""
    return Response(content=twiml, media_type="application/xml")


@app.get("/make-call")
def make_call():
    call = twilio_client.calls.create(
        to="+919080257430",
        from_=TWILIO_NUMBER,
        url="https://abactinal-laura-unowned.ngrok-free.dev/voice"
    )
    return {"status": "calling", "sid": call.sid}


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
        async with client.stream("POST", url, headers=headers, json={"text": text}) as r:
            buffer = b""
            async for raw_chunk in r.aiter_bytes():
                buffer += raw_chunk
                # Send complete 640-byte chunks immediately — don't wait for full response
                while len(buffer) >= TTS_CHUNK_BYTES:
                    piece = buffer[:TTS_CHUNK_BYTES]
                    buffer = buffer[TTS_CHUNK_BYTES:]
                    await twilio_ws.send_json({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": base64.b64encode(piece).decode()}
                    })
            # Send any remaining bytes
            if buffer:
                await twilio_ws.send_json({
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {"payload": base64.b64encode(buffer).decode()}
                })

    await twilio_ws.send_json({
        "event": "mark",
        "streamSid": stream_sid,
        "mark": {"name": "done"}
    })


async def llm_and_tts(transcript: str, twilio_ws: WebSocket, stream_sid: str):
    loop = asyncio.get_event_loop()
    try:
        completion = await loop.run_in_executor(None, lambda: groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful phone assistant. Respond in 1-2 short sentences."},
                {"role": "user", "content": transcript}
            ]
        ))
        reply = completion.choices[0].message.content.strip()
        print("AI:", reply)

        # Stream TTS directly — first audio bytes sent before full response is ready
        await stream_tts_to_twilio(reply, twilio_ws, stream_sid)

    except asyncio.CancelledError:
        pass  # barge-in: user interrupted
    except Exception as e:
        print("LLM/TTS ERROR:", e)


@app.websocket("/ws")
async def websocket_endpoint(twilio_ws: WebSocket):
    await twilio_ws.accept()
    print("Twilio connected")

    stream_sid  = None
    active_task = None
    audio_queue = asyncio.Queue()

    async def deepgram_sender(dg_ws):
        while True:
            chunk = await audio_queue.get()
            if chunk is None:
                break
            try:
                await dg_ws.send(chunk)
            except Exception:
                break

    async def deepgram_receiver(dg_ws):
        nonlocal active_task, stream_sid
        async for raw in dg_ws:
            try:
                msg        = json.loads(raw)
                alt        = msg.get("channel", {}).get("alternatives", [{}])[0]
                transcript = alt.get("transcript", "").strip()
                is_final   = msg.get("speech_final", False)

                if transcript and is_final:
                    print("USER:", transcript)
                    if active_task and not active_task.done():
                        active_task.cancel()
                    active_task = asyncio.create_task(
                        llm_and_tts(transcript, twilio_ws, stream_sid)
                    )
            except Exception as e:
                print("DG RECV ERROR:", e)

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
                raw   = await twilio_ws.receive_text()
                msg   = json.loads(raw)
                event = msg.get("event")

                if event == "start":
                    stream_sid = msg["start"]["streamSid"]
                    print(f"Stream started: {stream_sid}")

                elif event == "media":
                    audio = base64.b64decode(msg["media"]["payload"])
                    await audio_queue.put(audio)

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