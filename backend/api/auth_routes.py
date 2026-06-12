# backend/api/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.database import get_db, User
from backend.core.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # "candidate" or "referrer"


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # check role is valid
    if request.role not in ["candidate", "referrer"]:
        raise HTTPException(status_code=400, detail="Role must be candidate or referrer")

    # check email not already taken
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # create user
    user = User(
        id=str(uuid4()),
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role=request.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role})

    return {
        "message": "Registration successful",
        "user_id": user.id,
        "role": user.role,
        "access_token": token,
        "token_type": "bearer"
    }

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.id, "role": user.role})

    return {
        "message": "Login successful",
        "user_id": user.id,
        "role": user.role,
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(db: Session = Depends(get_db),
           token: str = Depends(__import__('fastapi').security.OAuth2PasswordBearer(tokenUrl='/auth/login'))):
    from backend.core.auth import get_current_user
    # handled via get_current_user in protected routes
    return {"message": "Use Authorization header with Bearer token"}
