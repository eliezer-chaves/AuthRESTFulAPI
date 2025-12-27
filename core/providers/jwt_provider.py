from datetime import datetime, timedelta, timezone
from jose import jwt
import os
import secrets
import hmac, hashlib
from jose import JWTError, ExpiredSignatureError
from fastapi import HTTPException
from logging_config import logger

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE = int(os.getenv("REFRESH_TOKEN_EXPIRE"))
COOKIE_SECRET = os.getenv("COOKIE_SECRET")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        
        
        raise HTTPException(
            status_code=401,
            detail={
                "type": "access_token_expired",
                "title": "Access Token Expired",
                "message": "Access token expired."
            }
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_token",
                "title": "Invalid Token",
                "message": "Invalid authentication token."
            }
        )

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)

def hash_refresh_token(token: str) -> str:
    return hmac.new(
        COOKIE_SECRET.encode(),
        token.encode(),
        hashlib.sha256
    ).hexdigest()

def get_refresh_token_expiration() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE)
