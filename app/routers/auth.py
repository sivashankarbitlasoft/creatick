from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)


@router.post("/login", response_model=schemas.UserOut)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    No JWT/token - as agreed, keep this simple. The Flutter app just stores
    the returned user object in local storage (e.g. shared_preferences) and
    treats its presence as "logged in" until the user logs out.
    """
    user = crud.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user


@router.post("/forgot-password", response_model=schemas.UserOut)
def forgot_password(payload: schemas.ForgotPassword, db: Session = Depends(get_db)):
    """Simple password reset endpoint. Expects the user's email and a new password.
    In a real system this would be a two-step flow with email verification; keep it
    simple here per project scope.
    """
    user = crud.reset_password_by_email(db, payload.email, payload.new_password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
