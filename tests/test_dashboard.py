"""
Tests for the /dashboard endpoint (Phase 6) - user grouping, message
counts, and partial phone number search.

Uses the shared isolated test database from conftest.py.
"""

from fastapi.testclient import TestClient

from app.main import app
from app import crud

client = TestClient(app)


def _seed(db, phone: str, count: int):
    for i in range(count):
        crud.save_message(db, phone, f"message {i}", f"reply {i}")


def test_dashboard_shows_correct_totals(db_session):
    _seed(db_session, "whatsapp:+923001111111", 2)
    _seed(db_session, "whatsapp:+923002222222", 1)

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "2" in response.text
    assert "3" in response.text


def test_dashboard_shows_message_count_per_user(db_session):
    _seed(db_session, "whatsapp:+923001111111", 2)

    response = client.get("/dashboard")
    assert "2 messages" in response.text


def test_dashboard_singular_message_label(db_session):
    _seed(db_session, "whatsapp:+923001111111", 1)

    response = client.get("/dashboard")
    assert "1 message" in response.text
    assert "1 messages" not in response.text


def test_dashboard_partial_phone_search_filters_correctly(db_session):
    _seed(db_session, "whatsapp:+923001111111", 1)
    _seed(db_session, "whatsapp:+923002222222", 1)

    response = client.get("/dashboard", params={"phone": "1111111"})
    assert "+923001111111" in response.text
    assert "+923002222222" not in response.text


def test_dashboard_empty_state_when_no_users():
    response = client.get("/dashboard")
    assert "No users found" in response.text