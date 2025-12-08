from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from infra.providers.hash_provider import hash_password
from infra.auth.auth_service import get_current_user
from infra.providers.jwt_provider import create_access_token
from infra.auth.cookie_manager import set_auth_cookie

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.usr_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.post("/signup", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, response: Response, db: Session = Depends(get_db)):

    exists = db.query(User).filter(User.usr_email == payload.usr_email).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email já cadastrado")

    new_user = User(
        usr_first_name=payload.usr_first_name,
        usr_last_name=payload.usr_last_name,
        usr_email=payload.usr_email,
        usr_password=hash_password(payload.usr_password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 🔥 LOGIN AUTOMÁTICO APÓS CADASTRO
    token = create_access_token({"sub": str(new_user.usr_id)})
    set_auth_cookie(response, token)

    return new_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.usr_id != user_id:
        raise HTTPException(status_code=403, detail="Apenas seu próprio usuário")

    user = db.query(User).filter(User.usr_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.usr_id != user_id:
        raise HTTPException(status_code=403, detail="Apenas seu próprio usuário")

    user = db.query(User).filter(User.usr_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(user)
    db.commit()
