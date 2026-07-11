"""
Tests for the /webhook and /history endpoints (Phases 2, 3, 5).

Uses the shared isolated test database from conftest.py, so these
tests never touch your real database.db.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_webhook_rule_based_command_returns_twiml():
    response = client.post(
        "/webhook",
        data={"From": "whatsapp:+923001234567", "Body": "Hi"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    assert "<Response>" in response.text
    assert "Hi there" in response.text


def test_webhook_escapes_special_xml_characters():
    with patch("app.bot.responder.get_ai_response") as mock_ai:
        mock_ai.return_value = "Use <b> tags & the > symbol carefully."
        response = client.post(
            "/webhook",
            data={"From": "whatsapp:+923001234567", "Body": "how do I use html tags"},
        )
    assert "&lt;b&gt;" in response.text
    assert "&amp;" in response.text
    assert "&gt;" in response.text
    assert "<b>" not in response.text


def test_webhook_persists_conversation_to_database():
    client.post(
        "/webhook",
        data={"From": "whatsapp:+923009999999", "Body": "Hi"},
    )
    client.post(
        "/webhook",
        data={"From": "whatsapp:+923009999999", "Body": "Time"},
    )

    history_response = client.get("/history/whatsapp:+923009999999")
    assert history_response.status_code == 200

    data = history_response.json()
    assert data["message_count"] == 2
    assert data["conversation"][0]["incoming_message"] == "Hi"
    assert data["conversation"][1]["incoming_message"] == "Time"


def test_webhook_keeps_different_users_separate():
    client.post("/webhook", data={"From": "whatsapp:+923001111111", "Body": "Hi"})
    client.post("/webhook", data={"From": "whatsapp:+923002222222", "Body": "Hi"})

    history_1 = client.get("/history/whatsapp:+923001111111").json()
    history_2 = client.get("/history/whatsapp:+923002222222").json()

    assert history_1["message_count"] == 1
    assert history_2["message_count"] == 1


def test_history_for_unknown_number_returns_empty():
    response = client.get("/history/whatsapp:+920000000000")
    assert response.status_code == 200
    assert response.json()["message_count"] == 0