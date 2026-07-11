"""
Tests for app/bot/rules.py - rule-based command matching (Phase 3).
"""

from app.bot.rules import get_rule_based_response


def test_greeting_variants_match():
    assert get_rule_based_response("Hi") is not None
    assert get_rule_based_response("hello") is not None
    assert get_rule_based_response("HEY") is not None


def test_case_and_whitespace_insensitive():
    response_lower = get_rule_based_response("help")
    response_upper = get_rule_based_response("  HELP  ")
    assert response_lower == response_upper


def test_time_command_returns_current_time_format():
    response = get_rule_based_response("Time")
    assert response is not None
    assert "current time is" in response.lower()


def test_date_command_returns_current_date_format():
    response = get_rule_based_response("Date")
    assert response is not None
    assert "today's date is" in response.lower()


def test_about_command_matches():
    response = get_rule_based_response("about")
    assert response is not None
    assert "chatbot" in response.lower()


def test_services_command_matches():
    response = get_rule_based_response("Services")
    assert response is not None
    assert "offer" in response.lower()


def test_unknown_message_returns_none():
    """
    No rule should match arbitrary text - this is what tells the
    responder to fall back to the AI handler.
    """
    assert get_rule_based_response("what's the weather like today") is None


def test_empty_message_returns_none():
    assert get_rule_based_response("") is None
    assert get_rule_based_response(None) is None