from datetime import datetime, timedelta, timezone
from jose import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    from jose import JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================
# 🔐 TOKEN EXCLUSIVO PARA RESET DE SENHA
# ============================================

def create_reset_token(user_id: int, code_id: int, expires_minutes: int = 10):
    """
    Gera um JWT curto e específico para reset de senha.
    Ele não autentica o usuário, só permite trocar a senha.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    payload = {
        "sub": str(user_id),
        "type": "password_reset",
        "code_id": str(code_id),
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_reset_token(token: str):
    """
    Decodifica e valida o token de reset.
    Retorna o payload se válido, senão None.
    Também garante que o type seja 'password_reset'.
    """
    from jose import JWTError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # evita uso indevido de token de login
        if payload.get("type") != "password_reset":
            return None

        return payload

    except JWTError:
        return None
