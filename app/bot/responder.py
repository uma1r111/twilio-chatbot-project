"""
Central place that decides how to respond to an incoming message.

Phase 3: tries rule-based commands first.
Phase 4 (later): will fall back to AI if no rule matches.
"""

from app.bot.rules import get_rule_based_response
from app.bot.ai_handler import get_ai_response


def get_bot_response(message: str) -> str:
    """
    Returns the text the bot should reply with, given the incoming message.
    Tries rule-based commands first, falls back to AI if no rule matches.
    """
    rule_response = get_rule_based_response(message)
    if rule_response is not None:
        return rule_response

    return get_ai_response(message)


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