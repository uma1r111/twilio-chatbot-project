"""
Phase 5 - CRUD operations for Users and Messages.
"""

from sqlalchemy.orm import Session

from app.models import User, Message


def get_or_create_user(db: Session, phone_number: str) -> User:
    """
    Fetches an existing user by phone number, or creates one if it
    doesn't exist yet.
    """
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if user is None:
        user = User(phone_number=phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def save_message(
    db: Session, phone_number: str, incoming_message: str, bot_response: str
) -> Message:
    """
    Stores one conversation turn: the user's incoming message and the
    bot's response, tied to the user's phone number, timestamped.
    """
    user = get_or_create_user(db, phone_number)

    message = Message(
        user_id=user.id,
        incoming_message=incoming_message,
        bot_response=bot_response,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_conversation_history(db: Session, phone_number: str) -> list[Message]:
    """
    Retrieves all messages for a given phone number, ordered oldest first.
    """
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if user is None:
        return []

    return (
        db.query(Message)
        .filter(Message.user_id == user.id)
        .order_by(Message.timestamp.asc())
        .all()
    )


def get_all_users(db: Session) -> list[User]:
    """Retrieves all users (used later by the Phase 6 dashboard)."""
    return db.query(User).all()


def get_all_messages(db: Session) -> list[Message]:
    """Retrieves all messages (used later by the Phase 6 dashboard)."""
    return db.query(Message).order_by(Message.timestamp.desc()).all()