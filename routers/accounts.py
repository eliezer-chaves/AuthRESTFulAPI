from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
# ===== Python standard library =====
import os
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta, timezone

# ===== Third-party libraries =====
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

# ===== Application infrastructure =====
from logging_config import logger
from database import get_db

# ===== Models =====
from models.user import User
from models.email_tokens import Token
from models.password_reset_code import PasswordResetCode

# ===== Schemas =====
from schemas.user import *

# ===== Providers =====
from core.providers.hash_provider import verify_password, hash_password
from core.providers.jwt_provider import create_access_token

# ===== Handlers =====
from core.handler.cookie_manager import (
    set_auth_cookie,
    clear_auth_cookie,
    get_token_from_cookie,
    create_cookie_registration_sended,
    create_cookie_code_valid,
    create_cookie_email_sended,
    clear_cookie_email_sended,
    clear_cookie_code_valid, 
    clear_cookie_registration_sended,
    delete_all_cookies,
    CookieReader
)

# ===== Services =====
from core.services.auth_service import token_blacklist, get_current_user
from core.services.email_service import (
    send_reset_code_email,
    send_confirmation_email,
)
from core.services import auth_service

# ===== Utils =====
from core.utils.generate_random_code import generate_reset_code
from core.utils.generate_email_token import generate_email_token
from core.utils.email_rate_limit import *
from core.utils.mask_email import mask_email


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)

@router.post("", status_code=201)
async def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    try:
        user_exists = db.query(User).filter(
            User.usr_email == payload.usr_email and
            User.usr_email_verified == False and
            User.usr_user_active == False
        ).first()


        if user_exists and user_exists.usr_email_verified == False and user_exists.usr_user_active == False:
            user_token = db.query(Token).filter(
                Token.ect_user_id == user_exists.usr_id
            ).first()

            if user_token:

                token = db.query(Token).filter(
                    Token.ect_id == user_token.ect_id
                ).first()

                expires_at = token.ect_expires_at.replace(tzinfo=timezone.utc)

                if datetime.now(timezone.utc) > expires_at:

                    db.delete(token)
                    db.commit()

                    email_token = generate_email_token()

                    new_token = Token(
                        ect_user_id=user_exists.usr_id,
                        ect_token=email_token,
                        ect_expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
                    )
                    db.add(new_token)
                    db.commit()

                    await send_confirmation_email(user_exists.usr_email, user_exists.usr_first_name, email_token)

                    create_cookie_registration_sended(email_token, response)

                    return {
                            "type": "new_token_generated",
                            "title": "New Token",
                            "message": "Check your mail box to validate your email."
                        }

                else:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "type": "token_already_exists_valid",
                            "title": "Token Already Exists",
                            "message": "Check your mail box to validate your email."
                        }
                    )

            else:

                email_token = generate_email_token()

                new_token = Token(
                    ect_user_id=user_exists.usr_id,
                    ect_token=email_token,
                    ect_expires_at=datetime.now(
                        timezone.utc) + timedelta(minutes=5)
                )
                db.add(new_token)
                db.commit()

                await send_confirmation_email(user_exists.usr_email, user_exists.usr_first_name, email_token)

                create_cookie_registration_sended(email_token, response)

                return {
                    "type": "new_token_generated",
                    "title": "New Token",
                    "message": "Check your mail box to validate your email."
                }
        
        if user_exists and user_exists.usr_email_verified == True and user_exists.usr_user_active == True:  
            raise HTTPException(status_code=409, detail={
                "type": "email_already_registered",
                "title": "This email is already registered.",
                "message": "Please try another or sign in.",
            })
            
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

        new_token = Token(
            ect_user_id=new_user.usr_id,
            ect_token=email_token,
            ect_expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )

        db.add(new_token)
        db.commit()

        await send_confirmation_email(new_user.usr_email, new_user.usr_first_name, email_token)

        create_cookie_registration_sended(email_token, response)

        return {
            "type": "email_sent",
            "title": "Email Sent",
            "message": "Confirm your email to get access to your account.",
        }
        

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error creating user: %s", str(e))
        raise HTTPException(status_code=500)


@router.post("/verification")
def validate_account(body: dict, response: Response, db: Session = Depends(get_db)):
    token_from_url = body.get("token")

    if not token_from_url:
        raise HTTPException(status_code=410, detail= {
            "type": "email_sent",
            "title": "Email Sent",
            "message": "Confirm your email to get access to your account.",
        })

    # Busca token no banco
    token_db = db.query(Token).filter(
        Token.ect_token == token_from_url).first()

    if not token_db:
        raise HTTPException(status_code=410, detail={
            "type": "token_not_found",
            "title": "Invalid or Expired Link",
            "message": "This confirmation link is no longer valid. Your email may already be verified. Please try logging in."})


    # Valida expiração
    expires_at=token_db.ect_expires_at
    if expires_at.tzinfo is None:
        expires_at=expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
        status_code=410,
        detail={
            "type": "email_confirmation_expired",
            "title": "Confirmation expired",
            "message": "Your account was not activated in time and has been removed. Please create a new account."
        }
    )

    # Pega o usuário associado
    user=token_db.ect_user

    # Atualiza status do usuário
    user.usr_email_verified=True
    user.usr_user_active=True
    db.add(user)
    db.commit()
    db.refresh(user)
    
    db.delete(token_db)
    db.commit()

    # Cria JWT e seta cookie (SEM try/except para ver erro real)
    jwt_token=create_access_token(
        {"sub": str(user.usr_id), "email": user.usr_email})
   

    set_auth_cookie(response, jwt_token)
    

    clear_cookie_registration_sended(response)
    
    return {
            "type": "user_created",
            "title": "Welcome!",
            "message": "Your account was created succesefully."
        }
    

@router.get("/verification/status")
def check_email_status(request: Request, db: Session = Depends(get_db)):
    
    cookie = CookieReader.get_cookie_registration_email_sended(request)
    
    if not cookie:
        raise HTTPException(status_code=403, detail={"access": "denied", "message": "not_found"})

    try:
        hashed_token, signature = cookie.split("|")
    except ValueError:
        raise HTTPException(status_code=401)

    expected = hmac.new(os.getenv("COOKIE_SECRET").encode(), hashed_token.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401)

    return {
        "email": "email sended",
    }

