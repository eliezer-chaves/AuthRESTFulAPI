from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.auth_models.user_model import User
from schemas.user_schema import UserLogin, UserResponse
from core.services.auth import auth_service
from core.handler.cookie_manager import get_token_from_cookie
from core.services.auth.auth_service import token_blacklist, get_current_user
from core.handler.cookie_manager import (
    clear_auth_cookie,
    get_token_from_cookie,
    delete_all_cookies,
    clear_refresh_cookie,
)
from models.auth_models.refresh_token_model import RefreshToken
from datetime import datetime, timedelta, timezone
from core.providers.jwt_provider import decode_access_token
from logging_config import logger

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

@router.post("")
def create_session_route(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    return auth_service.login(payload, response, db)

@router.delete("/current", status_code=204)
def delete_session_route(response: Response, token: str = Depends(get_token_from_cookie), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    token_blacklist.add(token)

    clear_auth_cookie(response)
    clear_refresh_cookie(response)
    delete_all_cookies(response)

    auth_service.revoke_refresh_tokens_by_user(db=db, user_id=current_user.usr_id)
   
@ router.get("/current", response_model=UserResponse)
def get_current_user_info_route(current_user: User=Depends(get_current_user)):
    return current_user
    
@router.post("/refresh")
def refresh_session(request: Request, response: Response,db: Session = Depends(get_db)):
    
    return auth_service.refresh_session(request, response, db)

@router.get("/status")
def debug_session(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return auth_service.debug_session(request, db, user)
