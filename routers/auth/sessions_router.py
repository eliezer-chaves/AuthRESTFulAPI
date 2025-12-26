from fastapi import APIRouter, Depends, Response, Request
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
)

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

@router.post("")
def create_session(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    auth_service.login(payload, response, db)


@ router.delete("/current", status_code=204)
def delete_session(response: Response, token: str=Depends(get_token_from_cookie)):
    token_blacklist.add(token)
    clear_auth_cookie(response)
    delete_all_cookies(response)    


@ router.get("/current", response_model=UserResponse)
def get_current_user_info(current_user: User=Depends(get_current_user)):
    return current_user
    
