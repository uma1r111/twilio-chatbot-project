"""
Phase 3 - Rule-Based Bot Logic

Matches incoming message text against known commands and returns a
canned response. Returns None if no rule matches, so the caller
(responder.py in Phase 4) knows to fall back to the AI handler.
"""

from datetime import datetime


def get_rule_based_response(message: str) -> str | None:
    """
    Match the incoming message against known commands (case-insensitive,
    whitespace-trimmed). Returns the matched response, or None if the
    message doesn't match any known command.
    """
    if not message:
        return None

    text = message.strip().lower()

    if text in ("hi", "hello", "hey"):
        return "Hi there! I'm your assistant bot. Type 'Help' to see what I can do."

    if text == "help":
        return (
            "Here are the commands I understand:\n"
            "- Hi: Greet me\n"
            "- Time: Get current time\n"
            "- Date: Get today's date\n"
            "- About: Learn about this bot\n"
            "- Services: See what services we offer"
        )

    if text == "time":
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."

    if text == "date":
        current_date = datetime.now().strftime("%B %d, %Y")
        return f"Today's date is {current_date}."

    if text == "about":
        return (
            "I'm a Python-based chatbot built with FastAPI, "
            "designed to demonstrate webhook handling, rule-based "
            "responses, and AI integration."
        )

    if text == "services":
        return (
            "We offer:\n"
            "1. Automated customer support\n"
            "2. AI-powered conversation handling\n"
            "3. Conversation history tracking\n"
            "Reply with a number to learn more, or type 'Help' for other commands."
        )

    # No rule matched
    return None