from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from infra.providers.hash_provider import hash_password

from logging_config import logger

router = APIRouter(prefix="/users", tags=["Users"])

# ✔ GET ALL - Retorna lista de UserResponse
@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users  # FastAPI converterá automaticamente usando UserResponse

# ✔ GET BY ID - Retorna UserResponse
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.usr_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )
    return user  # Retorna o objeto SQLAlchemy diretamente

# ✔ CREATE - Retorna UserResponse
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        # Verifica email duplicado
        exists = db.query(User).filter(User.usr_email == payload.usr_email).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email já cadastrado"
            )

        # Cria usuário com senha hash
        new_user = User(
            usr_first_name=payload.usr_first_name,
            usr_last_name=payload.usr_last_name,
            usr_email=payload.usr_email,
            usr_password=hash_password(payload.usr_password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user  # Retorna o objeto SQLAlchemy
    except HTTPException:
        raise  # Re-lança HTTPExceptions para que sejam tratadas corretamente
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar usuário"
        )

# ✔ UPDATE - Retorna UserResponse
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.usr_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )

    # Atualiza apenas os campos que foram fornecidos
    if payload.usr_first_name is not None:
        user.usr_first_name = payload.usr_first_name
    if payload.usr_last_name is not None:
        user.usr_last_name = payload.usr_last_name
    if payload.usr_email is not None:
        user.usr_email = payload.usr_email
    if payload.usr_password is not None:
        user.usr_password = hash_password(payload.usr_password)

    db.commit()
    db.refresh(user)

    return user  # Retorna o objeto SQLAlchemy

# ✔ DELETE - Retorna nada (204 No Content)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.usr_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )

    db.delete(user)
    db.commit()
    return