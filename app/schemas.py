from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import TicketStatus


# ---------- USER ----------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordVerify(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class ForgotPassword(BaseModel):
    email: EmailStr
    new_password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None  # only sent if user wants to change it


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    created_at: datetime


# ---------- TICKET ----------

# app_type accepts "android", "ios", or "both".
# "both" makes the service layer create TWO separate ticket rows.
class TicketCreate(BaseModel):
    operator_name: str
    sub_domain: str
    website: Optional[str] = None
    description: Optional[str] = None
    image_url_1: Optional[str] = None
    image_url_2: Optional[str] = None
    image_url_3: Optional[str] = None
    image_url_4: Optional[str] = None
    image_url_5: Optional[str] = None
    image_url_6: Optional[str] = None
    app_type: Literal["android", "ios", "both"]
    created_by: int  # id of the logged-in BA (sent from Flutter local storage)


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketUpdate(BaseModel):
    """Used by the Flask UI for a developer to edit full ticket details."""
    operator_name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    image_url_1: Optional[str] = None
    image_url_2: Optional[str] = None
    image_url_3: Optional[str] = None
    image_url_4: Optional[str] = None
    image_url_5: Optional[str] = None
    image_url_6: Optional[str] = None
    status: Optional[TicketStatus] = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: Optional[str]
    operator_name: str
    sub_domain: str
    website: Optional[str] = None
    description: Optional[str] = None
    image_url_1: Optional[str] = None
    image_url_2: Optional[str] = None
    image_url_3: Optional[str] = None
    image_url_4: Optional[str] = None
    image_url_5: Optional[str] = None
    image_url_6: Optional[str] = None
    app_type: str
    status: str
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
