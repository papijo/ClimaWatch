import logging
import secrets
from datetime import datetime, timezone

import resend
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.models.user_subscription import UserSubscription
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.jwt import create_access_token
from app.modules.auth.password import hash_password, verify_password

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY

router = APIRouter(prefix="/api/auth", tags=["auth"])
me_router = APIRouter(prefix="/api/me", tags=["me"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    locale: str = "en"
    target: str = "public"  # "public" or "admin"


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


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


@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email, User.is_active.is_(True)).first()
    if user:
        token_value = secrets.token_hex(32)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token_value,
        )
        db.add(reset_token)
        db.commit()
        if body.target == "admin":
            reset_url = f"{settings.ADMIN_URL}/reset-password?token={token_value}"
        else:
            reset_url = f"{settings.FRONTEND_URL}/{body.locale}/auth/reset-password?token={token_value}"
        _send_reset_email(user.email, user.full_name or "there", reset_url)
    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    record = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == body.token,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user = db.query(User).filter(User.id == record.user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user.password_hash = hash_password(body.new_password)
    record.used_at = now
    db.commit()
    return {"message": "Password updated successfully"}


def _send_reset_email(to_email: str, name: str, reset_url: str) -> None:
    html = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,Helvetica,sans-serif;margin:0;padding:0;background:#f9fafb;">
  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;background:#ffffff;">
    <tr>
      <td style="padding:24px 32px;background:#059669;color:#ffffff;">
        <h1 style="margin:0;font-size:20px;">ClimaWatch</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:32px;">
        <p style="margin:0 0 16px;font-size:14px;color:#6b7280;">Hello {name},</p>
        <h2 style="margin:0 0 12px;font-size:20px;color:#111827;">Reset your password</h2>
        <p style="margin:0 0 24px;font-size:14px;line-height:1.6;color:#374151;">
          We received a request to reset your ClimaWatch password. Click the button below to choose a new password.
          This link expires in 1 hour.
        </p>
        <a href="{reset_url}"
           style="display:inline-block;background:#059669;color:#ffffff;text-decoration:none;
                  padding:12px 28px;border-radius:8px;font-size:14px;font-weight:600;">
          Reset Password
        </a>
        <p style="margin:24px 0 0;font-size:13px;color:#9ca3af;">
          If you did not request a password reset, you can safely ignore this email.
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:16px 32px;background:#f1f5f9;text-align:center;">
        <p style="margin:0;font-size:12px;color:#94a3b8;">&copy; ClimaWatch by Serge Ltd. All rights reserved.</p>
      </td>
    </tr>
  </table>
</body>
</html>"""
    try:
        resend.Emails.send({
            "from": "ClimaWatch <hello@weareserge.com>",
            "to": [to_email],
            "subject": "Reset your ClimaWatch password",
            "html": html,
        })
    except Exception:
        logger.exception("Failed to send password reset email to %s", to_email)


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


@me_router.delete("/subscriptions/{state_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    state_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = (
        db.query(UserSubscription)
        .filter(
            UserSubscription.user_id == current_user.id,
            UserSubscription.state_id == state_id,
        )
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub.is_active = False
    db.commit()
    return None
