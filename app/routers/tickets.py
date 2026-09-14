from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=List[schemas.TicketOut])
def create_ticket(data: schemas.TicketCreate, db: Session = Depends(get_db)):
    """
    Creates the ticket(s). If app_type == 'both', this returns TWO tickets,
    each with its own id and ticket_number.
    """
    try:
        tickets = crud.create_tickets(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="A ticket with this sub-domain and app type already exists",
        )
    return tickets


@router.get("", response_model=List[schemas.TicketOut])
def list_tickets(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Dashboard tab calls this. Pass ?user_id=<id> to show only that BA's tickets,
    or omit it to show all tickets (e.g. for the Flask dev view).
    """
    if user_id is not None:
        return crud.get_tickets_by_user(db, user_id)
    return crud.get_tickets(db)


@router.get("/{ticket_number}", response_model=schemas.TicketOut)
def get_ticket(ticket_number: str, db: Session = Depends(get_db)):
    ticket = crud.get_ticket_by_number(db, ticket_number)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/{ticket_number}", response_model=schemas.TicketOut)
def update_ticket(ticket_number: str, data: schemas.TicketUpdate, db: Session = Depends(get_db)):
    """Full edit - used by the Flask developer UI, and by the Flutter update page."""
    ticket = crud.update_ticket(db, ticket_number, data)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_number}/status", response_model=schemas.TicketOut)
def update_status(ticket_number: str, data: schemas.TicketStatusUpdate, db: Session = Depends(get_db)):
    """Quick status-only update, e.g. a dropdown in the Flask ticket page."""
    ticket = crud.update_ticket_status(db, ticket_number, data.status)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.delete("/{ticket_number}", status_code=204)
def delete_ticket(ticket_number: str, db: Session = Depends(get_db)):
    """Deletes a ticket. Used by the dashboard card's 3-dot 'Delete ticket' menu item."""
    deleted = crud.delete_ticket(db, ticket_number)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return None