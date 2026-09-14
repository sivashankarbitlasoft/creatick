from typing import List, Optional

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------- USER ----------

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def reset_password_by_email(db: Session, email: str, new_password: str) -> Optional[models.User]:
    """Find user by email and update their password. Returns the user or None if not found."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    user.password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def update_user(db: Session, user_id: int, data: schemas.UserUpdate) -> Optional[models.User]:
    user = get_user(db, user_id)
    if not user:
        return None
    if data.name is not None:
        user.name = data.name
    if data.phone is not None:
        user.phone = data.phone
    if data.password:
        user.password = hash_password(data.password)
    db.commit()
    db.refresh(user)
    return user


# ---------- TICKET ----------

def _generate_ticket_number(ticket_id: int) -> str:
    return f"TCK-{ticket_id:06d}"


def _create_single_ticket(db: Session, data: schemas.TicketCreate, app_type: str) -> models.Ticket:
    db_ticket = models.Ticket(
        operator_name=data.operator_name,
        sub_domain=data.sub_domain,
        website=data.website,
        description=data.description,
        image_url_1=data.image_url_1,
        image_url_2=data.image_url_2,
        image_url_3=data.image_url_3,
        image_url_4=data.image_url_4,
        image_url_5=data.image_url_5,
        image_url_6=data.image_url_6,
        app_type=app_type,
        status=models.TicketStatus.to_do,
        created_by=data.created_by,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    # Fill in the human-readable ticket number now that we have an id
    db_ticket.ticket_number = _generate_ticket_number(db_ticket.id)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def create_tickets(db: Session, data: schemas.TicketCreate) -> List[models.Ticket]:
    """
    Creates 1 ticket for 'android' or 'ios', or 2 separate tickets (each with its
    own id/ticket_number) when app_type is 'both'.
    """
    if data.app_type == "both":
        ticket_android = _create_single_ticket(db, data, models.AppType.android)
        ticket_ios = _create_single_ticket(db, data, models.AppType.ios)
        return [ticket_android, ticket_ios]
    else:
        return [_create_single_ticket(db, data, data.app_type)]


def get_tickets(db: Session) -> List[models.Ticket]:
    return db.query(models.Ticket).order_by(models.Ticket.created_at.desc()).all()


def get_tickets_by_user(db: Session, user_id: int) -> List[models.Ticket]:
    return (
        db.query(models.Ticket)
        .filter(models.Ticket.created_by == user_id)
        .order_by(models.Ticket.created_at.desc())
        .all()
    )


def get_ticket_by_number(db: Session, ticket_number: str) -> Optional[models.Ticket]:
    return (
        db.query(models.Ticket)
        .filter(models.Ticket.ticket_number == ticket_number)
        .first()
    )


def update_ticket(db: Session, ticket_number: str, data: schemas.TicketUpdate) -> Optional[models.Ticket]:
    ticket = get_ticket_by_number(db, ticket_number)
    if not ticket:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_status(db: Session, ticket_number: str, status: models.TicketStatus) -> Optional[models.Ticket]:
    ticket = get_ticket_by_number(db, ticket_number)
    if not ticket:
        return None
    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return ticket
