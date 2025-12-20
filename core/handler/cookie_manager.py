import os
import hmac
import hashlib

from fastapi import Response, Request, HTTPException, status

# Config base do cookie — alterou aqui, vale pro sistema inteiro
BASE_COOKIE_CONFIG = {
    "key": "access_token",
    "httponly": True,
    "samesite": "none",
    "secure": True,
    "max_age": int(os.getenv("TOKEN_MAX_AGE")),
    "path": "/"
}

# ---------------------------
# FUNÇÕES DE COOKIE
# ---------------------------
def set_auth_cookie(response: Response, token: str):
    
    cfg = BASE_COOKIE_CONFIG.copy()
    cfg["value"] = token
    response.set_cookie(**cfg)


def clear_auth_cookie(response: Response):
    
    cfg = BASE_COOKIE_CONFIG.copy()
    cfg["value"] = ""
    cfg["max_age"] = 0
    response.set_cookie(**cfg)


def get_token_from_cookie(request: Request) -> str:
    
    token = request.cookies.get(BASE_COOKIE_CONFIG["key"])
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não encontrado no cookie"
        )
    return token

def create_cookie_registration_sended(email_token, response: Response):
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