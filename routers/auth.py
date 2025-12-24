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

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/debug/request-info")
async def debug_request_info(request: Request):
    client = request.client

    return {
        "ip": client.host,
        "port": client.port,
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "user_agent": request.headers.get("user-agent"),
    }







