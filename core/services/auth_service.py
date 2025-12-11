from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from core.providers.jwt_provider import decode_access_token
from core.handler.cookie_manager import get_token_from_cookie

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
