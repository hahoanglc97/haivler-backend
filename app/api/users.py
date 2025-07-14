from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..db import models, schemas
from ..core.security import get_current_user, get_password_hash, get_user_by_email

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if user_update.email:
        existing_user = get_user_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    if user_update.password:
        current_user.password_hash = get_password_hash(user_update.password)
    
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    db.commit()
    db.refresh(current_user)
    return current_user