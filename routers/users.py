from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from core.services.auth_service import get_current_user
from core.handler.cookie_manager import set_auth_cookie
from logging_config import logger

router = APIRouter(prefix="/users", tags=["Users"])


