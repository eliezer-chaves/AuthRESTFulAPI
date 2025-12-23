from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from core.providers.jwt_provider import decode_access_token
from core.handler.cookie_manager import get_token_from_cookie
from models import User
from schemas.user import UserLogin
from sqlalchemy.orm import Session
from fastapi import APIRouter,  HTTPException, Response, Request
from sqlalchemy.orm import Session
from core.providers.hash_provider import verify_password, hash_password
from core.providers.jwt_provider import create_access_token
from core.handler.cookie_manager import set_auth_cookie

token_blacklist = set()

def get_current_user(token: str = Depends(get_token_from_cookie), db: Session = Depends(get_db)) -> User:

    if token in token_blacklist:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_or_expired_token",
                "title": "Invalid or Expired Token",
                "message": "The provided authentication token is invalid or has expired."
            }
        )
        
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_token",
                "title": "Invalid Token",
                "message": "The authentication token provided is not valid."
            }
        )
    
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "invalid_token_payload",
                "title": "Invalid Token Payload",
                "message": "The token payload is missing required user information."
            }
        )

    user = db.query(User).filter(User.usr_id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "type": "user_not_found",
                "title": "User Not Found",
                "message": "No user exists for the authentication token provided."
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
    
    return {
            "type": "login_success",
            "title": "Login successful",
            "message": "You have logged in successfully."
        }