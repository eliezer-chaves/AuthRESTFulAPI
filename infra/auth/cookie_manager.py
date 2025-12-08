import os
from fastapi import Response, Request, HTTPException, status

# Config base do cookie — alterou aqui, vale pro sistema inteiro
BASE_COOKIE_CONFIG = {
    "key": "access_token",
    "httponly": True,
    "samesite": "none",
    "secure": True,
    "max_age": int(os.getenv("TOKEN_MAX_AGE", "3600")),
    "path": "/"
}

# ---------------------------
# FUNÇÕES DE COOKIE
# ---------------------------
def set_auth_cookie(response: Response, token: str):
    """Aplica o cookie JWT usando a configuração global."""
    cfg = BASE_COOKIE_CONFIG.copy()
    cfg["value"] = token
    response.set_cookie(**cfg)


def clear_auth_cookie(response: Response):
    """Remove o cookie do navegador."""
    cfg = BASE_COOKIE_CONFIG.copy()
    cfg["value"] = ""
    cfg["max_age"] = 0
    response.set_cookie(**cfg)


def get_token_from_cookie(request: Request) -> str:
    """Lê o token do cookie, já padronizado."""
    token = request.cookies.get(BASE_COOKIE_CONFIG["key"])
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não encontrado no cookie"
        )
    return token
