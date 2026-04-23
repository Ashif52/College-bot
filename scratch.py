from dotenv import load_dotenv
load_dotenv(override=True)
import os
from chatbot.voicebot_service import normalize_outbound_phone, build_voice_webhook_url, get_twilio_number

raw_phone = '9791867356'
session_id = 'test-1234'

to_number = normalize_outbound_phone(raw_phone)
voice_url = build_voice_webhook_url(session_id)
from_number = get_twilio_number()

print("to:", to_number)
print("from:", from_number)
print("url:", voice_url)
print("SID:", os.getenv("TWILIO_ACCOUNT_SID"))

from twilio.rest import Client
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

try:
    c = client.calls.create(to=to_number, from_=from_number, url=voice_url)
    print("Success:", c.sid)
except Exception as e:
    print("Error:", str(e))
