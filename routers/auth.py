from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserResponse
from infra.providers.hash_provider import verify_password
from infra.providers.jwt_provider import create_access_token, decode_access_token
from logging_config import logger
from fastapi import Response, Request   


router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
token_blacklist = set()


def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não encontrado no cookie"
        )

    return token

# --------------------------
# FUNÇÃO CENTRAL DE AUTH
# --------------------------
def get_current_user(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
) -> User:
    """
    Valida o token JWT e retorna o usuário autenticado.
    """

    # Blacklist
    if token in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    user = db.query(User).filter(User.usr_id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    return user

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

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="none",   # Para desenvolvimento local
        secure=True,      # False em HTTP local, True em produção HTTPS
        max_age=60 * 60 * 24,  # 24 horas
        path="/",
          # Adicione isso para desenvolvimento local
    )

    return {"message": "Login bem-sucedido", "user": UserResponse.from_orm(user)}


# --------------------------
# LOGOUT
# --------------------------
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(oauth2_scheme)):
    token_blacklist.add(token)
    return


# --------------------------
# INFO DO USUÁRIO
# --------------------------
# PARA ISSO:
@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Retorna as informações do usuário autenticado.
    O token deve vir do cookie, não do header.
    """
    return current_user

@router.get("/test-cookie")
def test_cookie(request: Request):
    """Endpoint para testar se o cookie está sendo recebido"""
    token = request.cookies.get("access_token")
    return {
        "cookie_received": token is not None,
        "cookie_value_length": len(token) if token else 0,
        "all_cookies": dict(request.cookies)
    }