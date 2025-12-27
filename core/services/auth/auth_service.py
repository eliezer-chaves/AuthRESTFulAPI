from fastapi import Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
import os
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from logging_config import logger
from database import get_db
from models.auth_models.user_model import User
from models.auth_models.email_tokens_model import Token
from schemas.user_schema import *
from core.providers.hash_provider import verify_password, hash_password
from core.providers.jwt_provider import create_access_token, decode_access_token
from core.handler.cookie_manager import (
    set_auth_cookie,
    get_token_from_cookie,
    create_cookie_registration_sended,
    clear_cookie_registration_sended,
    CookieReader,
    set_refresh_cookie,
    get_refresh_token_from_cookie
)
from core.services.email_service import send_confirmation_email
from core.utils.email_utils import *
from core.providers.jwt_provider import (
    generate_refresh_token,
    hash_refresh_token,
    get_refresh_token_expiration
)
from models.auth_models.refresh_token_model import RefreshToken


token_blacklist = set()


def get_current_user(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
) -> User:

    payload = decode_access_token(token)  
    
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_token_payload",
                "title": "Invalid Token Payload",
                "message": "Missing subject."
            }
        )

    user = db.query(User).filter(User.usr_id == int(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "user_not_found",
                "title": "User Not Found",
                "message": "User does not exist."
            }
        )

    return user


def login(payload: UserLogin, response: Response, db):
    
    email = payload.usr_email
    password = payload.usr_password
    
    if not email or not password:
        raise HTTPException(
        status_code=400,
        detail={
            "type": "missing_credentials",
            "title": "Missing credentials",
            "message": "Email and password are required."
        })

    user = db.query(User).filter(User.usr_email == email).first()

    if not user:
            raise HTTPException(
                status_code=401,
                detail={
                    "type": "user_not_found",
                    "title": "Email not found",
                    "message": "We couldn't find an account with this email address."
                })

    if user.usr_email_verified == False or user.usr_user_active == False:
            raise HTTPException(
                status_code=401,
                detail={
                    "type": "email_not_verified",
                    "title": "Email Not Verified",
                    "message": "Please confirm your email before logging in."
                })

    if not verify_password(password, user.usr_password):
            raise HTTPException(
                status_code=401,
                detail={
                    "type": "invalid_credentials",
                    "title": "Invalid credentials",
                    "message": "Incorrect email or password."
                })

    token = create_access_token(
            {
                "sub": str(user.usr_id), 
                "email": user.usr_email
            })
        
    set_auth_cookie(response, token)
    refresh_token = generate_refresh_token()

    db_refresh = RefreshToken(
        rft_user_id=user.usr_id,
        rft_hash_token=hash_refresh_token(refresh_token),
        rft_expires_at=get_refresh_token_expiration(),
        rft_created_at=datetime.now(timezone.utc),
        rft_last_used_at=datetime.now(timezone.utc)
    )

    db.add(db_refresh)
    db.commit()

    set_refresh_cookie(response, refresh_token)

    return {
            "type": "login_success",
            "title": "Login successful",
            "message": "You have logged in successfully."
        }
    
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

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "type": "internal_error",
                "title": "Internal Error",
                "message": "An error occurred while processing your request."
            }
        )

def validate_account(body: dict, response: Response, db: Session = Depends(get_db)):
    token_from_url = body.get("token")

    if not token_from_url:
        raise HTTPException(status_code=410, detail= {
            "type": "email_sent",
            "title": "Email Sent",
            "message": "Confirm your email to get access to your account.",
        })

    token_db = db.query(Token).filter(
        Token.ect_token == token_from_url).first()

    if not token_db:
        raise HTTPException(status_code=410, detail={
            "type": "token_not_found",
            "title": "Invalid or Expired Link",
            "message": "This confirmation link is no longer valid. Your email may already be verified. Please try logging in."
        })

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

    user=token_db.ect_user

    user.usr_email_verified=True
    user.usr_user_active=True
    db.add(user)
    db.commit()
    db.refresh(user)
    
    db.delete(token_db)
    db.commit()

    jwt_token=create_access_token( 
        {
            "sub": str(user.usr_id),
            "email": user.usr_email
        }
    )
   
    set_auth_cookie(response, jwt_token)
    
    clear_cookie_registration_sended(response)
    
    return {
            "type": "user_created",
            "title": "Welcome!",
            "message": "Your account was created succesefully."
        }
    
def check_email_status(request: Request, db: Session = Depends(get_db)):
    cookie = CookieReader.get_cookie_registration_email_sended(request)
    
    if not cookie:
        raise HTTPException(
            status_code=403,
            detail={
                "type": "email_status_not_authorized",
                "title": "Access Denied",
                "message": "No valid email registration status was found."
            }
        )

    try:
        hashed_token, signature = cookie.split("|")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_cookie_format",
                "title": "Invalid Cookie",
                "message": "The registration status cookie format is invalid."
            }
        )

    expected = hmac.new(os.getenv("COOKIE_SECRET").encode(), hashed_token.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_cookie_signature",
                "title": "Invalid Cookie",
                "message": "The registration status cookie signature is invalid."
            }
        )

    return {
        "type": "email_status_found",
        "title": "Email Status Available",
        "message": "The email registration status was successfully retrieved."
    }

def refresh_session(request: Request, response: Response, db: Session):
    
    raw_refresh = get_refresh_token_from_cookie(request)
    hashed = hash_refresh_token(raw_refresh)
    
    refresh = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.rft_hash_token == hashed,
            RefreshToken.rft_revoked_at.is_(None),
            RefreshToken.rft_expires_at > datetime.now(timezone.utc)
        )
        .first()
    )

    if not refresh:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_refresh_token",
                "title": "Invalid session",
                "message": "Your session has expired. Please log in again."
            }
        )
    
    # ✅ Revoga o refresh token antigo (rotation)
    refresh.rft_revoked_at = datetime.now(timezone.utc)

    new_refresh = generate_refresh_token()

    db_refresh = RefreshToken(
        rft_user_id=refresh.rft_user_id,
        rft_hash_token=hash_refresh_token(new_refresh),
        rft_expires_at=get_refresh_token_expiration(),
        rft_created_at=datetime.now(timezone.utc),
        rft_last_used_at=datetime.now(timezone.utc)
    )

    db.add(db_refresh)
    db.commit()
    
    access_token = create_access_token({
        "sub": str(refresh.rft_user_id)
    })

    set_auth_cookie(response, access_token)
    set_refresh_cookie(response, new_refresh)

    return {
        "type": "session_refreshed",
        "title": "Session refreshed",
        "message": "Your session was successfully renewed."
    }

def revoke_refresh_tokens_by_user(db: Session, user_id: int):
    db.query(RefreshToken).filter(
        RefreshToken.rft_user_id == user_id,
        RefreshToken.rft_revoked_at.is_(None)
    ).update(
        {"rft_revoked_at": datetime.now(timezone.utc)}
    )
    db.commit()

def debug_session(request, db: Session, user: User):
    try:
        # ===== Cookies =====
        cookies = request.cookies

        # ===== Access token =====
        token = get_token_from_cookie(request)
        payload = decode_access_token(token)

        now = datetime.now(timezone.utc)
        access_exp = datetime.fromtimestamp(
            payload["exp"], tz=timezone.utc
        )

        # ===== Refresh token =====
        refresh = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.rft_user_id == user.usr_id,
                RefreshToken.rft_revoked_at.is_(None)
            )
            .order_by(RefreshToken.rft_created_at.desc())
            .first()
        )

        refresh_expires_at = None
        refresh_expires_in = None

        if refresh:
            refresh_expires_at = refresh.rft_expires_at

            if refresh_expires_at.tzinfo is None:
                refresh_expires_at = refresh_expires_at.replace(
                    tzinfo=timezone.utc
                )

            refresh_expires_in = int(
                (refresh_expires_at - now).total_seconds()
            )

        return {
            "server_time": now.isoformat(),

            "access_token": {
                "expires_at": access_exp.isoformat(),
                "expires_in_seconds": int(
                    (access_exp - now).total_seconds()
                ),
            },

            "refresh_token": {
                "expires_at": (
                    refresh_expires_at.isoformat()
                    if refresh_expires_at else None
                ),
                "expires_in_seconds": refresh_expires_in,
            },

            "cookies_present": {
                "access_token": "access_token" in cookies,
                "refresh_token": "refresh_token" in cookies,
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        
        raise HTTPException(
            status_code=500,
            detail={
                "type": "debug_session_error",
                "title": "Session debug error",
                "message": "Unable to retrieve session debug information."
            }
        )
