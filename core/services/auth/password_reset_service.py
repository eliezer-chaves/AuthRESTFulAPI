import os
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from logging_config import logger
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

    except Exception as e:
        logger.error("error saving reset code: %s", str(e))
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

    # Sem código → invalid_or_expired_code
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
    expires_at=reset_code.psc_expires_at
    if expires_at.tzinfo is None:
        expires_at=expires_at.replace(tzinfo=timezone.utc)

    # Código expirado → invalid_or_expired_code
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail={
                "type": "invalid_or_expired_code",
                "title": "Invalid or expired code.",
                "message": "The verification code has expired."
            }
        )

    # Marca como usado
    reset_code.psc_used_at=datetime.now(timezone.utc)
    # Get code
    code=reset_code.psc_code
   
    create_cookie_code_valid(code, response)

    return {
        "type": "password_reset_code_verified",
        "title": "Code verified successfully.",
        "message": "The verification code is valid."
    }

def authorize_password_reset(request: Request, db: Session=Depends(get_db)):

    cookie = CookieReader.get_cookie_email_code_valid(request)
    
    if not cookie:
        raise HTTPException(status_code=403, detail="Reset not authorized")

    # 1️⃣ Estrutura do cookie
    try:
        code, signature=cookie.split("|")
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid reset token")

    # 2️⃣ Assinatura HMAC
    expected_signature=hmac.new(
        os.getenv("COOKIE_SECRET").encode(),
        code.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=403, detail="Invalid reset token")

    # 3️⃣ Reset válido no banco
    reset=(
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
            status_code=403, detail="Reset flow expired or invalid")

    reset.psc_used_at=datetime.now(timezone.utc)
    db.commit()

    return {
        "allowed": True,
        "expires_at": reset.psc_expires_at
    }

def get_password_reset_status(request: Request, db: Session=Depends(get_db)):
   
    cookie = CookieReader.get_cookie_email_sended_to_reset_password(request)

    if not cookie:
        raise HTTPException(status_code=403, detail={ "access": "denied", "message": "not_found"})

    try:
        reset_id, signature=cookie.split("|")
    except ValueError:
        raise HTTPException(status_code=401)

    expected=hmac.new(os.getenv("COOKIE_SECRET").encode(),
                        reset_id.encode(),
                        hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401)

    reset=(
        db.query(PasswordResetCode)
        .filter_by(psc_reset_id=reset_id)
        .first())

    if reset.psc_used_at is None:
        raise HTTPException(status_code=401, detail={
            "title": "cookie already used"
        })

    email=reset.usr_user.usr_email

    expires_at=reset.psc_expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401)

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
            detail="Missing password fields"
        )

    if usr_password != usr_password_confirmation:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    #cookie=request.cookies.get("code_valid")
    cookie = CookieReader.get_cookie_email_code_valid(request)

    if not cookie:
        raise HTTPException(
            status_code=403,
            detail="Reset not authorized"
        )

    try:
        code, signature=cookie.split("|")
    except ValueError:
        raise HTTPException(status_code=401)

    # 3️⃣ Valida assinatura do cookie
    expected=hmac.new(
        os.getenv("COOKIE_SECRET").encode(),
        code.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401)

    # 4️⃣ Busca reset (NÃO filtra por used_at)
    reset=(
        db.query(PasswordResetCode)
        .filter(PasswordResetCode.psc_code == code)
        .first()
    )

    if not reset:
        raise HTTPException(
            status_code=404,
            detail="Invalid reset flow"
        )

    # 5️⃣ Expiração
    expires_at=reset.psc_expires_at

    if expires_at.tzinfo is None:
        expires_at=expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail="Reset expired"
        )

    user=(
        db.query(User)
        .filter(User.usr_id == reset.psc_user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
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

