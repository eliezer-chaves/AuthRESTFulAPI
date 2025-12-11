from fastapi import APIRouter, Depends, HTTPException, Response
from logging_config import logger
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import *
from core.providers.hash_provider import verify_password, hash_password
from core.providers.jwt_provider import create_access_token
from core.handler.cookie_manager import set_auth_cookie, clear_auth_cookie, get_token_from_cookie
from core.services.auth_service import token_blacklist
from core.services.auth_service import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    try:
        email = payload.usr_email
        password = payload.usr_password
        
        if not email or not password:
            raise HTTPException(
                status_code=400,
                detail={
                    "type": "missing_credentials",
                    "title": "Missing Credentials",
                    "message": "Email and password are required."
                }
            )
        
        user = db.query(User).filter(User.usr_email == email).first()
        
        if user is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "type": "user_not_found",
                    "title": "Email Not Registered",
                    "message": "The email provided is not associated with any account."
                }
            )


        if not user or not verify_password(password, user.usr_password):
            raise HTTPException(
                status_code=401,
                detail={
                    "type": "invalid_credentials",
                    "title": "Invalid Credentials",
                    "message": "The email or password provided is incorrect, try again."
                }
            )

        token = create_access_token({"sub": str(user.usr_id), "email": user.usr_email})
        set_auth_cookie(response, token)

        return {
            "type": "user_logged_in_success",
            "title": "User Logged In",
            "message": "Logged in successfully."
        }


    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        logger.error("Error during login: %s", str(e))
        
        raise HTTPException(
            status_code=500,
            detail={
                "type": "internal_server_error",
                "title": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later."
            }
        )


@router.post("/signup", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    try:

        exists = db.query(User).filter(
            User.usr_email == payload.usr_email).first()

        if exists:
            raise HTTPException(
                status_code=409,
                detail={
                    "type": "email_already_registered",
                    "title": "This email is already registered.",
                    "message": "This email is already registered. Please try another email or sign in."
                })
            
        if payload.usr_phone:
            exists_phone = db.query(User).filter(
                User.usr_phone == payload.usr_phone
            ).first()

            if exists_phone:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "type": "phone_already_registered",
                        "title": "Phone Already Registered",
                        "message": "This phone number is already associated with an existing account."
                    }
                )
        

        new_user = User(
            usr_first_name=payload.usr_first_name,
            usr_last_name=payload.usr_last_name,
            usr_email=payload.usr_email,
            usr_password=hash_password(payload.usr_password),
            usr_phone=payload.usr_phone
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        token = create_access_token({"sub": str(new_user.usr_id)})
        set_auth_cookie(response, token)

        return {
            "type": "user_created_success",
            "title": "User Created Successfuly",
            "message": "User created successfully."
        }

    
    except Exception as e:
        logger.error("Error creating user: %s", str(e))

        raise HTTPException(
            status_code=500,
            detail={
                "type": "internal_server_error",
                "title": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later."
            })
    finally:
        db.close()


@router.post("/send-email-code")
def send_email_with_code(payload: UserEmail, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.usr_email == payload.usr_email).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "type": "user_not_found",
                "title": "User Not Found",
                "message": "No user found with the provided email."
            }
        )
    
    
    
    return {
        "type": "password_reset_email_sent",
        "title": "Password Reset Email Sent",
        "message": "If an account with that email exists, a password reset email has been sent."
    }


@router.post("/logout", status_code=204)
def logout(response: Response, token: str = Depends(get_token_from_cookie)):
    token_blacklist.add(token)
    clear_auth_cookie(response)
    return {
            "type": "user_logout_success",
            "title": "Logout Successfuly",
            "message": "User logout successfuly."
        }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

