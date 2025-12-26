import os
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.auth_models.user_model import User
from models.auth_models.password_reset_code_model import PasswordResetCode
from schemas.user_schema import UserEmail
from core.providers.hash_provider import hash_password
from core.handler.cookie_manager import (
    create_cookie_email_sended,
    create_cookie_code_valid,
    clear_cookie_email_sended,
    clear_cookie_code_valid,
    CookieReader,
)
from core.services.email_service import send_reset_code_email
from core.utils.email_utils import generate_reset_code, mask_email


async def request_password_reset(payload: UserEmail, response: Response, request: Request, db: Session=Depends(get_db)):
    user=db.query(User).filter(User.usr_email == payload.usr_email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "type": "user_not_found",
                "title": "User Not Found",
                "message": "No user found with the provided email."
            }
        )

    code=generate_reset_code()
    expiration_minutes=int(os.getenv("SHORT_LIVED_TTL_MINUTES"))

    try:
        reset_id=str(uuid.uuid4())

        reset_entry=PasswordResetCode(
            psc_user_id=user.usr_id,
            psc_code=code,
            psc_reset_id=reset_id,
            psc_expires_at=datetime.now(
                timezone.utc) + timedelta(minutes=expiration_minutes),
        )

        db.add(reset_entry)
        db.commit()
        db.refresh(reset_entry)

        await send_reset_code_email(email=user.usr_email, code=code, user_name=user.usr_first_name)

        create_cookie_email_sended(reset_id, response)
        
        return {
            "type": "email_code_sent",
            "title": "Code Sent",
            "message": "The recovery code has been sent to your email.",

        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "type": "internal_error",
                "title": "Internal Error",
                "message": "An error occurred while processing your request."
            }
        )

def verify_reset_code(body: dict, response: Response, request: Request, db: Session=Depends(get_db)):

    code=body.get("code")

    if not code:
        raise HTTPException(
            status_code=400,
            detail={
                "type": "invalid_or_expired_code",
                "title": "Invalid or expired code.",
                "message": "A valid verification code is required."
            }
        )

    reset_code=(
        db.query(PasswordResetCode)
        .filter(PasswordResetCode.psc_code == code)
        .first()
    )

    if not reset_code:
        raise HTTPException(status_code=404, detail={
            "type": "invalid_or_expired_code",
            "title": "Invalid code",
            "message": "A valid verification code is required."

        })

    if reset_code.psc_used_at is None:
        raise HTTPException(
            status_code=409,
            detail={
                "type": "reset_already_used",
                "title": "Reset already completed",
                "message": "This reset code has already been used."
            }
        )

    # Normalizar timezone
    if expires_at.tzinfo is None:
        expires_at=expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail={
                "type": "invalid_or_expired_code",
                "title": "Invalid or expired code.",
                "message": "The verification code has expired."
            }
        )

    reset_code.psc_used_at=datetime.now(timezone.utc)
    code=reset_code.psc_code
   
    create_cookie_code_valid(code, response)

    return {
        "type": "password_reset_code_verified",
        "title": "Code verified successfully.",
        "message": "The verification code is valid."
    }
    
def authorize_password_reset(request: Request, db: Session = Depends(get_db)):

    cookie = CookieReader.get_cookie_email_code_valid(request)
    
    if not cookie:
        raise HTTPException(
            status_code=403,
            detail={
                "type": "reset_not_authorized",
                "title": "Reset Not Authorized",
                "message": "No valid password reset authorization was found."
            }
        )

    try:
        code, signature = cookie.split("|")
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail={
                "type": "invalid_reset_token_format",
                "title": "Invalid Reset Token",
                "message": "The password reset token format is invalid."
            }
        )

    expected_signature = hmac.new(os.getenv("COOKIE_SECRET").encode(), code.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(
            status_code=403,
            detail={
                "type": "invalid_reset_token_signature",
                "title": "Invalid Reset Token",
                "message": "The password reset token signature is invalid."
            }
        )

    reset = (
        db.query(PasswordResetCode)
        .filter(
            PasswordResetCode.psc_code == code,
            PasswordResetCode.psc_used_at.is_not(None),
            PasswordResetCode.psc_expires_at > datetime.now(timezone.utc)
        )
        .first()
    )

    if not reset:
        raise HTTPException(
            status_code=403,
            detail={
                "type": "reset_flow_invalid_or_expired",
                "title": "Reset Flow Invalid",
                "message": "The password reset flow is invalid or has expired."
            }
        )

    reset.psc_used_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "allowed": True,
        "expires_at": reset.psc_expires_at
    }


def get_password_reset_status(request: Request, db: Session = Depends(get_db)):

    cookie = CookieReader.get_cookie_email_sended_to_reset_password(request)

    if not cookie:
        raise HTTPException(
            status_code=403,
            detail={
                "type": "reset_status_not_authorized",
                "title": "Access Denied",
                "message": "No active password reset request was found."
            }
        )

    try:
        reset_id, signature = cookie.split("|")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_reset_cookie",
                "title": "Invalid Reset Token",
                "message": "The password reset token format is invalid."
            }
        )

    expected = hmac.new(os.getenv("COOKIE_SECRET").encode(), reset_id.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(
            status_code=401,
            detail={
                "type": "reset_cookie_signature_invalid",
                "title": "Invalid Reset Token",
                "message": "The password reset token signature is invalid."
            }
        )

    reset = (
        db.query(PasswordResetCode)
        .filter_by(psc_reset_id=reset_id)
        .first()
    )

    if reset.psc_used_at is None:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "reset_flow_not_verified",
                "title": "Reset Code Not Verified",
                "message": "The password reset code has not been verified yet."
            }
        )

    email = reset.usr_user.usr_email

    expires_at = reset.psc_expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail={
                "type": "reset_flow_expired",
                "title": "Password Reset Expired",
                "message": "The password reset request has expired."
            }
        )

    return {
        "email": mask_email(email),
        "expires_at": expires_at
    }


def update_password(body: dict, request: Request, response: Response, db: Session=Depends(get_db)):
    usr_password=body.get("usr_password")
    usr_password_confirmation=body.get("usr_password_confirmation")

    if not usr_password or not usr_password_confirmation:
        raise HTTPException(
            status_code=400,
            detail={
                "type": "missing_password_fields",
                "title": "Missing Password Fields",
                "message": "Both password and password confirmation are required."
            }
        )

    if usr_password != usr_password_confirmation:
        raise HTTPException(
            status_code=400,
            detail={
                "type": "passwords_do_not_match",
                "title": "Passwords Do Not Match",
                "message": "The password and confirmation password must be the same."
            }
        )

    cookie = CookieReader.get_cookie_email_code_valid(request)

    if not cookie:
        raise HTTPException(
            status_code=403,
            detail={
                "type": "password_reset_not_authorized",
                "title": "Password Reset Not Authorized",
                "message": "You are not authorized to reset the password. Please restart the password reset process."
            }
    )

    try:
        code, signature = cookie.split("|")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_reset_cookie_format",
                "title": "Invalid Reset Token",
                "message": "The password reset token format is invalid."
            }
        )

    expected=hmac.new(os.getenv("COOKIE_SECRET").encode(), code.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_reset_cookie_signature",
                "title": "Invalid Reset Token",
                "message": "The password reset token is invalid or has been tampered with."
            }
        )

    reset=(
        db.query(PasswordResetCode)
        .filter(PasswordResetCode.psc_code == code)
        .first()
    )

    if not reset:
        raise HTTPException(
            status_code=404,
            detail={
                "type": "reset_flow_not_found",
                "title": "Invalid Password Reset Flow",
                "message": "The password reset process could not be found or is no longer valid."
            }
        )

    expires_at=reset.psc_expires_at

    if expires_at.tzinfo is None:
        expires_at=expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail={
                "type": "reset_flow_expired",
                "title": "Password Reset Expired",
                "message": "The password reset link or code has expired. Please request a new one."
            }
        )

    user=(
        db.query(User)
        .filter(User.usr_id == reset.psc_user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "type": "user_not_found",
                "title": "User Not Found",
                "message": "No user was found for the provided password reset information."
            }
        )

    user.usr_password=hash_password(usr_password)

    reset.psc_used_at=datetime.now(timezone.utc)

    db.commit()

    clear_cookie_email_sended(response)
    clear_cookie_code_valid(response)

    return {
        "type": "password_updated",
        "title": "Password updated",
        "message": "Your password has been updated successfully."
    }

