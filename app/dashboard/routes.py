"""
Phase 6 - Simple Dashboard (Optional)

Shows total users, total messages, and a list of users with their
conversation counts. Each user row can be expanded to see their full
message history. Supports filtering by (partial) phone number.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud

router = APIRouter()
templates = Jinja2Templates(directory="app/dashboard/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_home(
    request: Request, phone: str = "", db: Session = Depends(get_db)
):
    """
    Renders the dashboard: total stats + a list of users, each showing
    their message count with an expandable section for full history.
    If `phone` is given, filters users by partial phone number match.
    """
    total_users = len(crud.get_all_users(db))
    total_messages = len(crud.get_all_messages(db))

    users = crud.get_users_with_conversations(db, phone_filter=phone)

    # Sort each user's messages oldest-first for readable conversation flow
    user_rows = [
        {
            "phone_number": u.phone_number,
            "message_count": len(u.messages),
            "messages": sorted(u.messages, key=lambda m: m.timestamp),
        }
        for u in users
    ]

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "total_users": total_users,
            "total_messages": total_messages,
            "user_rows": user_rows,
            "search_phone": phone,
        },
    )