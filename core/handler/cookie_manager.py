import os
import hmac
import hashlib
from fastapi import Response, Request, HTTPException, status

# =========================
# Base config
# =========================

BASE_COOKIE_CONFIG = {
    "httponly": True,
    "samesite": "none",
    "secure": True,
    "path": "/",
}

SHORT_LIVED_COOKIE_MAX_AGE = int(os.getenv("SHORT_LIVED_TTL_MINUTES")) * 60
AUTH_COOKIE_MAX_AGE = int(os.getenv("AUTH_COOKIE_MAX_AGE"))

# =========================
# Cookie configs
# =========================

COOKIE_AUTH_CONFIG = {
    **BASE_COOKIE_CONFIG,
    "key": "access_token",
    "max_age": AUTH_COOKIE_MAX_AGE,
}

COOKIE_REGISTRATION_SENDED_CONFIG = {
    **BASE_COOKIE_CONFIG,
    "key": "registration_sended",
    "max_age": SHORT_LIVED_COOKIE_MAX_AGE,
}

COOKIE_EMAIL_SENDED_CONFIG = {
    **BASE_COOKIE_CONFIG,
    "key": "mail_sended",
    "max_age": SHORT_LIVED_COOKIE_MAX_AGE,
}

COOKIE_CODE_VALID_CONFIG = {
    **BASE_COOKIE_CONFIG,
    "key": "code_valid",
    "max_age": SHORT_LIVED_COOKIE_MAX_AGE,
}

# Coleção explícita (serve para bulk operations)
ALL_COOKIE_CONFIGS = (
    COOKIE_AUTH_CONFIG,
    COOKIE_REGISTRATION_SENDED_CONFIG,
    COOKIE_EMAIL_SENDED_CONFIG,
    COOKIE_CODE_VALID_CONFIG,
)

# =========================
# Helpers internos
# =========================

def _set_cookie(response: Response, config: dict, value: str):
    cfg = config.copy()
    cfg["value"] = value
    response.set_cookie(**cfg)

def _clear_cookie(response: Response, config: dict):
    cfg = config.copy()
    cfg["value"] = ""
    cfg["max_age"] = 0
    response.set_cookie(**cfg)

def _signed_value(raw_value: str) -> str:
    signature = hmac.new(
        os.getenv("COOKIE_SECRET").encode(),
        raw_value.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{raw_value}|{signature}"

# =========================
# Auth cookie
# =========================

def set_auth_cookie(response: Response, token: str):
    _set_cookie(response, COOKIE_AUTH_CONFIG, token)

def clear_auth_cookie(response: Response):
    _clear_cookie(response, COOKIE_AUTH_CONFIG)

def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get(COOKIE_AUTH_CONFIG["key"])
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "authentication_error",
                "title": "Authentication Error",
                "message": "Security credentials could not be found or have expired. Please refresh the page and try again."
            })
    return token

# =========================
# Short-lived cookies
# =========================

def create_cookie_registration_sended(email_token: str, response: Response):
    _set_cookie(
        response,
        COOKIE_REGISTRATION_SENDED_CONFIG,
        _signed_value(email_token)
    )

def clear_cookie_registration_sended(response: Response):
    _clear_cookie(response, COOKIE_REGISTRATION_SENDED_CONFIG)

def create_cookie_email_sended(reset_id: str, response: Response):
    _set_cookie(
        response,
        COOKIE_EMAIL_SENDED_CONFIG,
        _signed_value(reset_id)
    )

def clear_cookie_email_sended(response: Response):
    _clear_cookie(response, COOKIE_EMAIL_SENDED_CONFIG)

def create_cookie_code_valid(code: str, response: Response):
    _set_cookie(
        response,
        COOKIE_CODE_VALID_CONFIG,
        _signed_value(code)
    )

def clear_cookie_code_valid(response: Response):
    _clear_cookie(response, COOKIE_CODE_VALID_CONFIG)

# =========================
# Bulk operation
# =========================

def delete_all_cookies(response: Response):
    for cfg in ALL_COOKIE_CONFIGS:
        _clear_cookie(response, cfg)
