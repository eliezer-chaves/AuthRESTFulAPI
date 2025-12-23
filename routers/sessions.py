from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from logging_config import logger
from database import get_db
from schemas.user import UserLogin, UserResponse
from core.services import auth_service
from core.handler.cookie_manager import get_token_from_cookie
from fastapi import APIRouter, Depends, HTTPException, Response, Request

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

@router.post("")
def create_session(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    try:
        auth_service.login(payload, response, db)

        return {
            "type": "login_success",
            "title": "Login successful",
            "message": "You have logged in successfully."
        }

    except Exception as e:
        logger.error("Error during login: %s", str(e))
        raise HTTPException(status_code=500, detail={
            "type": "login_error",
            "title": "Server Error",
            "message": "An error occurred during login. Please try again later."
        })



    
