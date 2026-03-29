from fastapi import FastAPI, Request,WebSocket
from fastapi.responses import Response
from twilio.rest import Client
from groq import Groq
import json
from deepgram import DeepgramClient
import base64
account_sid = "AC49ddcc92a93b10e1bea0620f1bf8e2a6"
auth_token = "b7bf453241751ef97461e7ae80aab978"
client = Client(account_sid, auth_token)

TWILIO_NUMBER= "+15822641391"

app = FastAPI()
# Questions list
questions = [
    "What is your name?",
    "What is your age?",
    "What city do you live in?"
]
# store answers
answers = {}
# 1️⃣ Endpoint Twilio calls when the phone answers
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


# 2️⃣ Endpoint to trigger the outbound call
@app.api_route("/make-call",methods=["GET","POST"])
def make_call():

    call = client.calls.create(
        to="+919080257430",      # target phone number
        from_=TWILIO_NUMBER,
        url="https://abactinal-laura-unowned.ngrok-free.dev/voice"
    )

    return {"status": "calling", "call_sid": call.sid}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    print("Twilio connected")

    while True:

        data = await ws.receive_text()
        message = json.loads(data)

        if message["event"] == "media":

            audio_base64 = message["media"]["payload"]
            audio_bytes = base64.b64decode(audio_base64)
            transcript = speech_to_text(audio_bytes)

            # send audio to STT

            if transcript:

                response = ask_llm(transcript)

                audio = text_to_speech(response)

                await ws.send_bytes(audio)

# 2️⃣ Handle answers and ask next question
@app.api_route("/handle-answer", methods=["POST"])
async def handle_answer(request: Request):

    step = int(request.query_params.get("step"))

    form = await request.form()
    speech = form.get("SpeechResult")

    print(f"Answer {step+1}: {speech}")

    answers[step] = speech

    next_step = step + 1

    # If more questions remain
    if next_step < len(questions):

        next_q = questions[next_step]

        twiml = f"""
<Response>
    <Gather input="speech" action="/handle-answer?step={next_step}" method="POST">
        <Say>{next_q}</Say>
    </Gather>
</Response>
"""

    else:
        print("All Answers:", answers)

        twiml = """
<Response>
    <Say>Thank you. Your responses have been recorded.</Say>
</Response>
"""

    return Response(content=twiml, media_type="application/xml")


dg = DeepgramClient(api_key="728abef073a3aeccff5e37849aa01bcb8810f237")

def speech_to_text(audio_bytes):

    try:
        response = dg.listen.v1.media.transcribe_file(
            request=audio_bytes,
            model="nova-3"
        )

        return response.results.channels[0].alternatives[0].transcript

    except Exception as e:
        print("STT error:", e)
        return None




groq_client = Groq(api_key="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")

def ask_llm(text):

    chat = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":"You are a helpful phone assistant"},
            {"role":"user","content":text}
        ]
    )

    return chat.choices[0].message.content