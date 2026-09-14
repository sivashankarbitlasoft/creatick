import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class AppType(str, enum.Enum):
    android = "android"
    ios = "ios"


class TicketStatus(str, enum.Enum):
    to_do = "to-do"
    in_progress = "in-progress"
    dev_done = "dev-done"
    closed = "closed"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password = Column(String(255), nullable=False)  # bcrypt hash, never plaintext
    created_at = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="creator")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        # Same operator can have an android AND ios ticket, but not two of the same type.
        UniqueConstraint("sub_domain", "app_type", name="uq_subdomain_apptype"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ticket_number = Column(String(20), unique=True, index=True, nullable=True)

    operator_name = Column(String(150), nullable=False)
    sub_domain = Column(String(100), nullable=False)
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    image_url_1 = Column(String(500), nullable=True)
    image_url_2 = Column(String(500), nullable=True)
    image_url_3 = Column(String(500), nullable=True)
    image_url_4 = Column(String(500), nullable=True)
    image_url_5 = Column(String(500), nullable=True)
    image_url_6 = Column(String(500), nullable=True)

    app_type = Column(Enum(AppType), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.to_do, nullable=False)

    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User", back_populates="tickets")
