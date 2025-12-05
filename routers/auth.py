from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserResponse
from infra.providers.hash_provider import verify_password
from infra.providers.jwt_provider import create_access_token, decode_access_token
from logging_config import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme para extrair token do header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Blacklist de tokens (em produção, use Redis ou banco de dados)
token_blacklist = set()

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica usuário e retorna access token.
    - **username**: email do usuário
    - **password**: senha do usuário
    """
    # Busca usuário por email
    user = db.query(User).filter(User.usr_email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.usr_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria token com dados do usuário
    access_token = create_access_token(
        data={
            "sub": str(user.usr_id),
            "email": user.usr_email
        }
    )
    
    logger.info(f"Usuário {user.usr_email} autenticado com sucesso")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(oauth2_scheme)):
    """
    Invalida o token atual (logout).
    """
    # Adiciona token à blacklist
    token_blacklist.add(token)
    logger.info("Token invalidado com sucesso")
    return


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(lambda token=Depends(oauth2_scheme), db=Depends(get_db): get_current_user(token, db))
):
    """
    Retorna informações do usuário autenticado.
    """
    return current_user


# Dependency para obter usuário autenticado
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Valida token JWT e retorna usuário autenticado.
    Pode ser usado como dependency em outras rotas protegidas.
    """
    # Verifica se token está na blacklist
    if token in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decodifica token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extrai user_id do token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Busca usuário no banco
    user = db.query(User).filter(User.usr_id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user