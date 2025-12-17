# ===== Python standard library =====
import os
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta, timezone

# ===== Third-party libraries =====
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
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
from core.providers.jwt_provider import create_access_token, create_reset_token

# ===== Handlers =====
from core.handler.cookie_manager import (
    set_auth_cookie,
    clear_auth_cookie,
    get_token_from_cookie,
)

# ===== Services =====
from core.services.auth_service import token_blacklist, get_current_user
from core.services.email_service import (
    send_reset_code_email,
    send_confirmation_email,
)

# ===== Utils =====
from core.utils.generate_random_code import generate_reset_code
from core.utils.generate_email_token import generate_email_token
from core.utils.email_rate_limit import *
from core.utils.mask_email import mask_email


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    try:
        email = payload.usr_email
        password = payload.usr_password

        if not email or not password:
            raise HTTPException(status_code=400)

        user = db.query(User).filter(User.usr_email == email).first()

        if (user.usr_email_verified == 0 or user.usr_user_active == 0 ):
            raise HTTPException(status_code=401, detail={
                "type": "email_not_verified",
                "title": "Email Not Verified",
                "message": "Confirm your email before login."
            })
        
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
async def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
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
        
        new_token = Token(
            ect_user_id = new_user.usr_id,
            ect_token = email_token,
            ect_expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        )
        db.add(new_token)
        db.commit()
        
        await send_confirmation_email(new_user.usr_email, new_user.usr_first_name, email_token)
        
        signature = hmac.new(os.getenv("COOKIE_SECRET").encode(), email_token.encode(), hashlib.sha256).hexdigest()

        cookie_value = f"{email_token}|{signature}"

        response.set_cookie(
            key="registration_sended",
            value=cookie_value,
            max_age=int(os.getenv("COOKIE_EXPIRRATION_TIME")),
            path="/",
            httponly=True,
            secure=True,
            samesite="none"
        )

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


@router.get("/has-cookie-registration")
def check_cookie(request: Request, db: Session = Depends(get_db)):
    cookie = request.cookies.get("registration_sended")

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


@router.post("/confirm-account")
def validate_account(body: dict, response: Response, db: Session = Depends(get_db)):
    token_from_url = body.get("token")

    if not token_from_url:
        raise HTTPException(status_code=400, detail="Token não fornecido")

    token_from_url

    # Busca token no banco
    token_db = db.query(Token).filter(Token.ect_token == token_from_url).first()

    if not token_db:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    # Valida expiração
    expires_at = token_db.ect_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expirado")

    # Pega o usuário associado
    user = token_db.ect_user
    print(f"👤 Usuário: {user.usr_id} - {user.usr_email}")

    # Atualiza status do usuário
    user.usr_email_verified = True
    user.usr_user_active = True
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ Usuário ativado: verified={user.usr_email_verified}, active={user.usr_user_active}")
    db.delete(token_db)
    db.commit()

    # Cria JWT e seta cookie (SEM try/except para ver erro real)
    jwt_token = create_access_token({"sub": str(user.usr_id), "email": user.usr_email})
    print(f"🎫 JWT criado: {jwt_token}")
    
    set_auth_cookie(response, jwt_token)
    print(f"🍪 Cookie setado no response")

    return {"detail": "Conta verificada com sucesso"}
    
@router.post("/validate-code")
def validate_code(body: dict, response: Response, request: Request, db: Session = Depends(get_db)):

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
    .filter(PasswordResetCode.psc_code == code)
    .first()
    )

    if not reset_code:
        raise HTTPException(status_code=404, detail={
                "type": "invalid_or_expired_code",
                "title": "Invalid code",
                "message": "A valid verification code is required."

            })

    if reset_code.psc_used_at is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "type": "reset_already_used",
                "title": "Reset already completed",
                "message": "This reset code has already been used."
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
    # Get code
    code = reset_code.psc_code

    signature = hmac.new(os.getenv("COOKIE_SECRET").encode(), code.encode(), hashlib.sha256).hexdigest()

    cookie_value = f"{code}|{signature}"

    response.set_cookie(
            key="code_valid",
            value=cookie_value,
            max_age=int(os.getenv("COOKIE_EXPIRRATION_TIME")),
            path="/",
            httponly=True,
            secure=True,
            samesite="none"
    )

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


@router.get("/code-valid")
def allow_reset_password(request: Request, db: Session = Depends(get_db)):

    cookie = request.cookies.get("code_valid")

    if not cookie:
        raise HTTPException(status_code=403, detail="Reset not authorized")

    # 1️⃣ Estrutura do cookie
    try:
        code, signature = cookie.split("|")
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid reset token")

    # 2️⃣ Assinatura HMAC
    expected_signature = hmac.new(
        os.getenv("COOKIE_SECRET").encode(),
        code.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=403, detail="Invalid reset token")

    # 3️⃣ Reset válido no banco
    reset = (
        db.query(PasswordResetCode)
        .filter(
            PasswordResetCode.psc_code == code,
            PasswordResetCode.psc_used_at.is_(None),
            PasswordResetCode.psc_expires_at > datetime.now(timezone.utc)
        )
        .first()
    )


    if not reset:
        raise HTTPException(status_code=403, detail="Reset flow expired or invalid")

    reset.psc_used_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "allowed": True,
        "expires_at": reset.psc_expires_at
    }

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

    if reset.psc_used_at is not None:
        raise HTTPException(status_code=401, detail={
            "title": "cookie already used"
        })

    email = reset.usr_user.usr_email

    expires_at = reset.psc_expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401)


    return {
        "email": mask_email(email),
        "expires_at": expires_at
    }

@router.post("/update-password")
def update_password(body: dict, request: Request,response: Response, db: Session = Depends(get_db)):
    usr_password = body.get("usr_password")
    usr_password_confirmation = body.get("usr_password_confirmation")


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

    cookie = request.cookies.get("code_valid")

    if not cookie:
        raise HTTPException(
            status_code=403,
            detail="Reset not authorized"
        )

    try:
        code, signature = cookie.split("|")
    except ValueError:
        raise HTTPException(status_code=401)

    # 3️⃣ Valida assinatura do cookie
    expected = hmac.new(
        os.getenv("COOKIE_SECRET").encode(),
        code.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401)

    # 4️⃣ Busca reset (NÃO filtra por used_at)
    reset = (
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
    expires_at = reset.psc_expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail="Reset expired"
        )


    user = (
        db.query(User)
        .filter(User.usr_id == reset.psc_user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # 8️⃣ Atualiza senha
    user.usr_password = hash_password(usr_password)

    # 9️⃣ Marca reset como usado
    reset.psc_used_at = datetime.now(timezone.utc)

    db.commit()

    response.delete_cookie(
        key="code_valid",
        path="/"
    )

    response.delete_cookie(
        key="mail_sended",
        path="/"
    )
    return {
        "type": "password_updated",
        "title": "Password updated",
        "message": "Your password has been updated successfully."
    }


@router.post("/logout", status_code=204)
def logout(response: Response, token: str = Depends(get_token_from_cookie)):
    token_blacklist.add(token)
    clear_auth_cookie(response)
    
    response.delete_cookie(
        key="registration_sended",
        path="/",
        httponly=True,
        secure=True,
        samesite="none"
    )
    return {
        "type": "user_logout_success",
        "title": "Logout Successfuly",
        "message": "User logout successfuly."
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
