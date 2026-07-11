"""
Tests for app/bot/ai_handler.py - AI fallback + conversation memory (Phase 4).

These mock the Azure OpenAI client so tests run without real credentials
or network calls.
"""

from unittest.mock import MagicMock, patch

import app.bot.ai_handler as ai_handler


def _make_mock_response(text: str):
    """Builds a fake OpenAI response object matching the shape our code reads."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = text
    return mock_response


@patch("app.bot.ai_handler._get_client")
@patch("app.bot.ai_handler.config")
def test_returns_reply_text_on_success(mock_config, mock_get_client):
    mock_config.AZURE_OPENAI_API_KEY = "fake-key"
    mock_config.ENDPOINT_URL = "https://fake-endpoint"
    mock_config.DEPLOYMENT_NAME = "gpt-4o-mini"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_mock_response(
        "Tokyo is the capital of Japan."
    )
    mock_get_client.return_value = mock_client

    result = ai_handler.get_ai_response("What is the capital of Japan?")
    assert result == "Tokyo is the capital of Japan."


@patch("app.bot.ai_handler._get_client")
@patch("app.bot.ai_handler.config")
def test_missing_credentials_returns_fallback_message(mock_config, mock_get_client):
    mock_config.AZURE_OPENAI_API_KEY = None
    mock_config.ENDPOINT_URL = None

    result = ai_handler.get_ai_response("Hello")
    assert "isn't configured" in result
    # Should never attempt to build a client if credentials are missing
    mock_get_client.assert_not_called()


@patch("app.bot.ai_handler._get_client")
@patch("app.bot.ai_handler.config")
def test_empty_model_response_returns_friendly_fallback(mock_config, mock_get_client):
    mock_config.AZURE_OPENAI_API_KEY = "fake-key"
    mock_config.ENDPOINT_URL = "https://fake-endpoint"
    mock_config.DEPLOYMENT_NAME = "gpt-4o-mini"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_mock_response("")
    mock_get_client.return_value = mock_client

    result = ai_handler.get_ai_response("Hello")
    assert "couldn't come up with a response" in result


@patch("app.bot.ai_handler._get_client")
@patch("app.bot.ai_handler.config")
def test_unexpected_exception_is_caught_and_returns_fallback(
    mock_config, mock_get_client
):
    mock_config.AZURE_OPENAI_API_KEY = "fake-key"
    mock_config.ENDPOINT_URL = "https://fake-endpoint"
    mock_config.DEPLOYMENT_NAME = "gpt-4o-mini"

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("boom")
    mock_get_client.return_value = mock_client

    result = ai_handler.get_ai_response("Hello")
    assert "unexpected" in result.lower()


@patch("app.bot.ai_handler._get_client")
@patch("app.bot.ai_handler.config")
def test_conversation_history_is_included_in_message_list(mock_config, mock_get_client):
    """
    Confirms history turns are correctly converted into alternating
    user/assistant messages, with the new message appended last.
    """
    mock_config.AZURE_OPENAI_API_KEY = "fake-key"
    mock_config.ENDPOINT_URL = "https://fake-endpoint"
    mock_config.DEPLOYMENT_NAME = "gpt-4o-mini"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_mock_response("Umair.")
    mock_get_client.return_value = mock_client

    history = [
        {"incoming_message": "My name is Umair", "bot_response": "Nice to meet you!"}
    ]
    ai_handler.get_ai_response("What's my name?", history=history)

    sent_messages = mock_client.chat.completions.create.call_args.kwargs["messages"]

    # system, user (history), assistant (history), user (current)
    assert sent_messages[0]["role"] == "system"
    assert sent_messages[1] == {"role": "user", "content": "My name is Umair"}
    assert sent_messages[2] == {"role": "assistant", "content": "Nice to meet you!"}
    assert sent_messages[-1] == {"role": "user", "content": "What's my name?"}