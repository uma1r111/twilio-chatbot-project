from fastapi import FastAPI, Form, Response

app = FastAPI(title="Mock Twilio Chatbot")

@app.post("/webhook")
async def twilio_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    # 1. Capture and log the incoming mock data (Phase 1 Learning)
    print(f"\n[Incoming Message] From: {From} | Body: {Body}")
    
    # 2. Implement Echo Logic (Phase 2)
    # Twilio demands a specific XML wrapper called TwiML to send a reply back.
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Echo: {Body}</Message>
</Response>"""

    # 3. Return the XML response with the correct media type
    return Response(content=twiml_response, media_type="application/xml")