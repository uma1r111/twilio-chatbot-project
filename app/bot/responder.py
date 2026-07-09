"""
Central place that decides how to respond to an incoming message.

Phase 3: tries rule-based commands first.
Phase 4: falls back to AI if no rule matches, using recent conversation
history for context.
"""

from sqlalchemy.orm import Session

from app.bot.rules import get_rule_based_response
from app.bot.ai_handler import get_ai_response
from app import crud

HISTORY_TURN_LIMIT = 5


def get_bot_response(message: str, phone_number: str, db: Session) -> str:
    """
    Returns the text the bot should reply with, given the incoming message.
    Tries rule-based commands first (stateless, no history needed).
    Falls back to AI with recent conversation history if no rule matches.
    """
    rule_response = get_rule_based_response(message)
    if rule_response is not None:
        return rule_response

    recent_messages = crud.get_recent_history(
        db, phone_number, limit=HISTORY_TURN_LIMIT
    )
    history = [
        {
            "incoming_message": m.incoming_message,
            "bot_response": m.bot_response,
        }
        for m in recent_messages
    ]

    return get_ai_response(message, history=history)


def build_twiml_response(reply_text: str) -> str:
    """
    Wraps a plain text reply in the TwiML XML format Twilio expects.
    """
    # Escape XML special characters so bot/user text doesn't break the XML.
    escaped = (
        reply_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{escaped}</Message>
</Response>"""