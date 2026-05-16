from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.user_subscription import UserSubscription
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.jwt import create_access_token
from app.modules.auth.password import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])
me_router = APIRouter(prefix="/api/me", tags=["me"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SubscriptionRequest(BaseModel):
    state_id: str
    notify_moderate: bool = False
    notify_high: bool = True
    notify_critical: bool = True


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email, User.is_active.is_(True)).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(user.id, user.role), "token_type": "bearer"}


@me_router.get("/subscriptions")
def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == current_user.id, UserSubscription.is_active.is_(True))
        .all()
    )


@me_router.post("/subscriptions", status_code=status.HTTP_201_CREATED)
def create_subscription(
    body: SubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == current_user.id, UserSubscription.state_id == body.state_id)
        .first()
    )
    if existing:
        existing.notify_moderate = body.notify_moderate
        existing.notify_high = body.notify_high
        existing.notify_critical = body.notify_critical
        existing.is_active = True
        db.commit()
        return existing
    sub = UserSubscription(
        user_id=current_user.id,
        state_id=body.state_id,
        notify_moderate=body.notify_moderate,
        notify_high=body.notify_high,
        notify_critical=body.notify_critical,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub
