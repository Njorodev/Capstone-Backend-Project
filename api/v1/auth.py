from fastapi import APIRouter, Depends, HTTPException, Request 
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from core import security
import crud
from schemas import user
from api.limiter import limiter # Import the limiter instance from limiter file

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=user.UserOut)
def register(user_in: user.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user_in)

@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request, # Requirement for slowapi
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}