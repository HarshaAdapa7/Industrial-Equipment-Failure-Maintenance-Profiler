from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.db.supabase_client import get_db
from app.db.models import Organization, User

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    org_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User email already registered")

    org = Organization(name=req.org_name)
    db.add(org)
    db.commit()
    db.refresh(org)

    # Simplified password hash for demo
    user = User(org_id=org.id, email=req.email, hashed_password=f"hashed_{req.password}")
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "ok": True,
        "org_id": org.id,
        "user_id": user.id,
        "access_token": f"mock_token_{user.id}"
    }

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "ok": True,
        "org_id": user.org_id,
        "user_id": user.id,
        "access_token": f"mock_token_{user.id}"
    }
