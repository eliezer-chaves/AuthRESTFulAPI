from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from logging_config import logger
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import *
from core.providers.hash_provider import verify_password, hash_password
from core.providers.jwt_provider import create_access_token, create_reset_token
from core.handler.cookie_manager import set_auth_cookie, clear_auth_cookie, get_token_from_cookie
from core.services.auth_service import token_blacklist
from core.services.auth_service import get_current_user
from core.utils.generate_random_code import generate_reset_code
from datetime import datetime, timedelta
import os
from core.services.email_service import send_reset_code_email
from models.password_reset_code import PasswordResetCode
from core.utils.email_rate_limit import *
import hmac
import hashlib
from core.utils.mask_email import mask_email
from core.utils.generate_email_token import generate_email_token, hash_token
import uuid


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    try:
        email = payload.usr_email
        password = payload.usr_password

        if not email or not password:
            raise HTTPException(status_code=400)

        user = db.query(User).filter(User.usr_email == email).first()

        if not user or not verify_password(password, user.usr_password):
            raise HTTPException(status_code=401)

        token = create_access_token({"sub": str(user.usr_id), "email": user.usr_email})
        set_auth_cookie(response, token)

        return {"message": "Logged in successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error during login: %s", str(e))
        raise HTTPException(status_code=500)


@router.post("/signup", status_code=201)
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    try:
        exists = db.query(User).filter(User.usr_email == payload.usr_email).first()
        if exists:
            raise HTTPException(status_code=409)

        new_user = User(
            usr_first_name=payload.usr_first_name,
            usr_last_name=payload.usr_last_name,
            usr_email=payload.usr_email,
            usr_password=hash_password(payload.usr_password),
            usr_phone=payload.usr_phone,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        email_token = generate_email_token()
        email_token_hash = hash_token(email_token)

        token = create_access_token({"sub": str(new_user.usr_id)})
        set_auth_cookie(response, token)

        return {"message": "User created successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error creating user: %s", str(e))
        raise HTTPException(status_code=500)


@router.post("/validate-code")
def validate_code(body: dict, response: Response, request: Request, db: Session = Depends(get_db)):
    code = body.get("code")

    if not code:
        raise HTTPException(status_code=400)

    reset_code = db.query(PasswordResetCode).filter(
        PasswordResetCode.psc_code == code
    ).first()

    if not reset_code or reset_code.psc_used_at is not None:
        raise HTTPException(status_code=404)

    if reset_code.psc_expires_at < datetime.utcnow():
        raise HTTPException(status_code=410)

    reset_code.psc_used_at = datetime.utcnow()

    signature = hmac.new(
        os.getenv("COOKIE_SECRET").encode(),
        code.encode(),
        hashlib.sha256
    ).hexdigest()

    response.set_cookie(
        key="code_valid",
        value=f"{code}|{signature}",
        max_age=int(os.getenv("COOKIE_EXPIRRATION_TIME")),
        httponly=True,
        secure=True,
        samesite="none"
    )

    return {"message": "Code verified successfully"}


@router.post("/send-reset-code")
async def send_reset_code(payload: UserEmail, response: Response, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.usr_email == payload.usr_email).first()
    if not user:
        raise HTTPException(status_code=404)

    code = generate_reset_code()
    expiration_minutes = int(os.getenv("MAIL_EXPIRATION_CODE_MINUTRES"))
    reset_id = str(uuid.uuid4())

    reset_entry = PasswordResetCode(
        psc_user_id=user.usr_id,
        psc_code=code,
        psc_reset_id=reset_id,
        psc_expires_at=datetime.utcnow() + timedelta(minutes=expiration_minutes),
    )

    db.add(reset_entry)
    db.commit()

    await send_reset_code_email(user.usr_email, code, user.usr_first_name)

    signature = hmac.new(
        os.getenv("COOKIE_SECRET").encode(),
        reset_id.encode(),
        hashlib.sha256
    ).hexdigest()

    response.set_cookie(
        key="mail_sended",
        value=f"{reset_id}|{signature}",
        max_age=int(os.getenv("COOKIE_EXPIRRATION_TIME")),
        httponly=True,
        secure=True,
        samesite="none"
    )

    return {"message": "Code sent"}


@router.get("/code-valid")
def allow_reset_password(request: Request, db: Session = Depends(get_db)):
    cookie = request.cookies.get("code_valid")
    if not cookie:
        raise HTTPException(status_code=403)

    code, signature = cookie.split("|")

    expected = hmac.new(
        os.getenv("COOKIE_SECRET").encode(),
        code.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=403)

    reset = db.query(PasswordResetCode).filter(
        PasswordResetCode.psc_code == code,
        PasswordResetCode.psc_used_at.is_(None),
        PasswordResetCode.psc_expires_at > datetime.utcnow()
    ).first()

    if not reset:
        raise HTTPException(status_code=403)

    reset.psc_used_at = datetime.utcnow()
    db.commit()

    return {"allowed": True, "expires_at": reset.psc_expires_at}


@router.post("/update-password")
def update_password(body: dict, request: Request, response: Response, db: Session = Depends(get_db)):
    cookie = request.cookies.get("code_valid")
    if not cookie:
        raise HTTPException(status_code=403)

    code, signature = cookie.split("|")

    expected = hmac.new(
        os.getenv("COOKIE_SECRET").encode(),
        code.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401)

    reset = db.query(PasswordResetCode).filter(
        PasswordResetCode.psc_code == code
    ).first()

    if not reset or reset.psc_expires_at < datetime.utcnow():
        raise HTTPException(status_code=410)

    user = db.query(User).filter(User.usr_id == reset.psc_user_id).first()
    user.usr_password = hash_password(body["usr_password"])
    reset.psc_used_at = datetime.utcnow()

    db.commit()

    response.delete_cookie("code_valid")
    response.delete_cookie("mail_sended")

    return {"message": "Password updated"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
