from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from infra.providers.hash_provider import hash_password
from infra.auth.auth_service import get_current_user
from infra.providers.jwt_provider import create_access_token
from infra.auth.cookie_manager import set_auth_cookie
from logging_config import logger

router = APIRouter(prefix="/users", tags=["Users"])


