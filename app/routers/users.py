from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_profile(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
