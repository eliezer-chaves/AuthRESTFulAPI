from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserResponse
from infra.providers.hash_provider import verify_password
from infra.providers.jwt_provider import create_access_token
from infra.auth.cookie_manager import set_auth_cookie, clear_auth_cookie, get_token_from_cookie
from infra.auth.auth_service import token_blacklist
from infra.auth.auth_service import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(data: dict, response: Response, db: Session = Depends(get_db)):
    email = data.get("usr_email")
    password = data.get("usr_password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email e senha são obrigatórios")

    user = db.query(User).filter(User.usr_email == email).first()

    if not user or not verify_password(password, user.usr_password):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    token = create_access_token({"sub": str(user.usr_id), "email": user.usr_email})

    set_auth_cookie(response, token)

    return {"message": "Login bem-sucedido", "user": UserResponse.from_orm(user)}


@router.post("/logout", status_code=204)
def logout(
    response: Response,
    token: str = Depends(get_token_from_cookie)
):
    token_blacklist.add(token)
    clear_auth_cookie(response)
    return


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/test-cookie")
def test_cookie(request: Request):
    token = request.cookies.get("access_token")
    return {
        "cookie_received": token is not None,
        "cookie_length": len(token) if token else 0,
        "cookies": dict(request.cookies)
    }
