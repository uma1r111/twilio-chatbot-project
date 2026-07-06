from fastapi import FastAPI, Form, Response

from app.bot.responder import get_bot_response, build_twiml_response

app = FastAPI(title="Mock Twilio Chatbot")


@app.post("/webhook")
async def twilio_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    # 1. Log the incoming message
    print(f"\n[Incoming Message] From: {From} | Body: {Body}")

    # 2. Phase 3: Get rule-based (or fallback) response
    reply_text = get_bot_response(Body)

    # 3. Wrap in TwiML and return
    twiml_response = build_twiml_response(reply_text)
    return Response(content=twiml_response, media_type="application/xml")