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
from datetime import timedelta, timezone
import os
from core.services.email_service import send_reset_code_email
from models.password_reset_code import PasswordResetCode
from core.utils.email_rate_limit import *
import hmac
import hashlib
from core.utils.mask_email import mask_email
import uuid


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    try:
        email = payload.usr_email
        password = payload.usr_password

        if not email or not password:
            raise HTTPException(
                status_code=400,
                detail={
                    "type": "missing_credentials",
                    "title": "Missing Credentials",
                    "message": "Email and password are required."
                }
            )

        user = db.query(User).filter(User.usr_email == email).first()

        if user is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "type": "user_not_found",
                    "title": "Email Not Registered",
                    "message": "The email provided is not associated with any account."
                }
            )

        if not user or not verify_password(password, user.usr_password):
            raise HTTPException(
                status_code=401,
                detail={
                    "type": "invalid_credentials",
                    "title": "Invalid Credentials",
                    "message": "The email or password provided is incorrect, try again."
                }
            )

        token = create_access_token(
            {"sub": str(user.usr_id), "email": user.usr_email})
        set_auth_cookie(response, token)

        return {
            "type": "user_logged_in_success",
            "title": "User Logged In",
            "message": "Logged in successfully."
        }

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        logger.error("Error during login: %s", str(e))

        raise HTTPException(
            status_code=500,
            detail={
                "type": "internal_server_error",
                "title": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later."
            }
        )


@router.post("/signup", status_code=201)
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    try:
        # Verifica email duplicado
        exists = db.query(User).filter(
            User.usr_email == payload.usr_email
        ).first()

        if exists:
            raise HTTPException(
                status_code=409,
                detail={
                    "type": "email_already_registered",
                    "title": "This email is already registered.",
                    "message": "This email is already registered. Please try another email or sign in."
                }
            )

        if payload.usr_phone:
            exists_phone = db.query(User).filter(
                User.usr_phone == payload.usr_phone
            ).first()

            if exists_phone:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "type": "phone_already_registered",
                        "title": "Phone Already Registered",
                        "message": "This phone number is already associated with an existing account."
                    }
                )

        # Cria usuário
        new_user = User(
            usr_first_name=payload.usr_first_name,
            usr_last_name=payload.usr_last_name,
            usr_email=payload.usr_email,
            usr_password=hash_password(payload.usr_password),
            usr_phone=payload.usr_phone
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Gera cookie JWT
        token = create_access_token({"sub": str(new_user.usr_id)})
        set_auth_cookie(response, token)

        return {
            "type": "user_created_success",
            "title": "User Created Successfully",
            "message": "User created successfully."
        }

    #  IMPORTANTE: preserva erros levantados manualmente
    except HTTPException as e:
        raise e

    #  Só cai aqui se for algo realmente inesperado
    except Exception as e:
        logger.error("Unexpected error creating user: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "type": "internal_server_error",
                "title": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later."
            }
        )


@router.post("/validate-code")
def validate_code(body: dict, response: Response, db: Session = Depends(get_db)):
    code = body.get("code")

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

    reset_code = (
        db.query(PasswordResetCode)
        .filter(
            PasswordResetCode.psc_code == code,
            PasswordResetCode.psc_used_at.is_(None)
        )
        .first()
    )

    # Código não encontrado → no_reset_code_found
    if not reset_code:
        raise HTTPException(
            status_code=404,
            detail={
                "type": "no_reset_code_found",
                "title": "Code not found.",
                "message": "No valid reset code was found."
            }
        )

    # Normalizar timezone
    expires_at = reset_code.psc_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

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
    reset_code.psc_used_at = datetime.now(timezone.utc)
    db.commit()

    # Sucesso → password_reset_code_verified
    return {
        "type": "password_reset_code_verified",
        "title": "Code verified successfully.",
        "message": "The verification code is valid."
    }


@router.post("/send-reset-code")
async def send_reset_code(payload: UserEmail, response: Response, request: Request, db: Session = Depends(get_db)):
    # Verifica rate limiting ANTES de qualquer outra operação
    rate_limit_info = await check_rate_limit(payload.usr_email, request, db)

    if rate_limit_info and rate_limit_info.get("blocked"):
        raise HTTPException(
            status_code=429,  # Too Many Requests
            detail={
                "type": "rate_limit_exceeded",
                "title": "Too Many Requests",
                "message": f"You have exceeded the maximum number of email requests. Please try again in {rate_limit_info['remaining_minutes']} minutes.",
                "blocked_until": rate_limit_info["blocked_until"],
                "remaining_seconds": rate_limit_info["remaining_seconds"],
                "remaining_minutes": rate_limit_info["remaining_minutes"],
                "attempts": rate_limit_info["attempts"]
            }
        )

    user = db.query(User).filter(User.usr_email == payload.usr_email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "type": "user_not_found",
                "title": "User Not Found",
                "message": "No user found with the provided email."
            }
        )

    code = generate_reset_code()
    expiration_minutes = int(os.getenv("MAIL_EXPIRATION_CODE_MINUTRES"))

    try:
        reset_id = str(uuid.uuid4())

        reset_entry = PasswordResetCode(
            psc_user_id=user.usr_id,
            psc_code=code,
            psc_reset_id=reset_id,
            psc_expires_at=datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes),
        )

        db.add(reset_entry)
        db.commit()
        db.refresh(reset_entry)

        await send_reset_code_email(email=user.usr_email, code=code, user_name=user.usr_first_name)

        signature = hmac.new(os.getenv("COOKIE_SECRET").encode(),
                            reset_id.encode(),
                            hashlib.sha256).hexdigest()

        cookie_value = f"{reset_id}|{signature}"

        response.set_cookie(
            key="mail_sended",
            value=cookie_value,
            max_age=int(os.getenv("COOKIE_EXPIRRATION_TIME")),
            path="/",
            httponly=True,
            secure=True,
            samesite="none"
        )

        return {
            "type": "email_code_sent",
            "title": "Code Sent",
            "message": "The recovery code has been sent to your email.",
            # "data": {
            #     "email": user.usr_email
            # }
        }

        # Adiciona informações de rate limit se disponíveis
        if rate_limit_info and not rate_limit_info.get("blocked"):
            response["rate_limit"] = {
                "attempts": rate_limit_info["attempts"],
                "max_attempts": rate_limit_info["max_attempts"],
                "remaining_attempts": rate_limit_info["remaining_attempts"]
            }

        return response

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


@router.get("/has-cookie")
def check_cookie(request: Request, db: Session = Depends(get_db)):
    cookie = request.cookies.get("mail_sended")

    if not cookie:
        raise HTTPException(status_code=403, detail={"access": "denied", "message": "not_found"})

    try:
        reset_id, signature = cookie.split("|")
    except ValueError:
        raise HTTPException(status_code=401)
    
    expected = hmac.new(os.getenv("COOKIE_SECRET").encode(),
                        reset_id.encode(),
                        hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401)
    
    reset = (
        db.query(PasswordResetCode)
        .filter_by(psc_reset_id=reset_id)
        .first())
    
    email = reset.usr_user.usr_email
    
    expires_at = reset.psc_expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401)

    
    return {
        "email": mask_email(email),
        "expires_at": expires_at
    }  


@router.post("/logout", status_code=204)
def logout(response: Response, token: str = Depends(get_token_from_cookie)):
    token_blacklist.add(token)
    clear_auth_cookie(response)
    return {
        "type": "user_logout_success",
        "title": "Logout Successfuly",
        "message": "User logout successfuly."
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
