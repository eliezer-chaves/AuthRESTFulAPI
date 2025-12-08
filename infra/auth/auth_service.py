from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from infra.providers.jwt_provider import decode_access_token
from infra.auth.cookie_manager import get_token_from_cookie

token_blacklist = set()

def get_current_user(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
) -> User:

    if token in token_blacklist:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.usr_id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user
