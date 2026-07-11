from fastapi import FastAPI, Form, Response, Depends
from sqlalchemy.orm import Session

from app.bot.responder import get_bot_response, build_twiml_response
from app.database import Base, engine, get_db
from app import crud
from app.dashboard.routes import router as dashboard_router

# Creates users/messages tables on startup if they don't already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mock Twilio Chatbot")
app.include_router(dashboard_router)


@app.post("/webhook")
async def twilio_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db),
):
    # 1. Log the incoming message
    print(f"\n[Incoming Message] From: {From} | Body: {Body}")

    # 2. Get rule-based (or AI fallback with conversation history) response
    reply_text = get_bot_response(Body, From, db)

    # 3. Phase 5: persist this conversation turn
    crud.save_message(
        db, phone_number=From, incoming_message=Body, bot_response=reply_text
    )

    # 4. Wrap in TwiML and return
    twiml_response = build_twiml_response(reply_text)
    return Response(content=twiml_response, media_type="application/xml")


@app.get("/history/{phone_number}")
async def conversation_history(phone_number: str, db: Session = Depends(get_db)):
    """
    Retrieves full conversation history for a given phone number.
    Example: GET /history/+923001234567
    """
    messages = crud.get_conversation_history(db, phone_number)
    return {
        "phone_number": phone_number,
        "message_count": len(messages),
        "conversation": [
            {
                "incoming_message": m.incoming_message,
                "bot_response": m.bot_response,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in messages
        ],
    }