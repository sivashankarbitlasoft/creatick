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


@router.post("/forgot-password")
def forgot_password(payload: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_code = crud.generate_otp_code()
    crud.save_password_otp(db, user.email, otp_code)

    try:
        crud.send_password_reset_otp_email(user.email, otp_code)
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to send OTP email") from exc

    return {"message": "OTP sent to your email address.", "email": user.email}


@router.post("/forgot-password/verify", response_model=schemas.UserOut)
def verify_forgot_password(payload: schemas.ForgotPasswordVerify, db: Session = Depends(get_db)):
    user = crud.reset_password_with_otp(db, payload.email, payload.otp, payload.new_password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return user
