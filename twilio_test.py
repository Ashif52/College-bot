from twilio.rest import Client

account_sid = "AC49ddcc92a93b10e1bea0620f1bf8e2a6"
auth_token = "b7bf453241751ef97461e7ae80aab978"
client = Client(account_sid, auth_token)

call = client.calls.create(
    to="+919080257430",
    from_="+15822641391",
    url="http://demo.twilio.com/docs/voice.xml"
)

print(call.sid)