from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

# ✔ GET ALL
@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# ✔ GET BY ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.usr_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return user

# ✔ CREATE
@router.post("/", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    # impedir email duplicado
    exists = db.query(User).filter(User.usr_email == payload.usr_email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    new_user = User(
        usr_first_name=payload.usr_first_name,
        usr_last_name=payload.usr_last_name,
        usr_email=payload.usr_email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ✔ UPDATE
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.usr_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.usr_first_name = payload.usr_first_name
    user.usr_last_name = payload.usr_last_name
    user.usr_email = payload.usr_email

    db.commit()
    db.refresh(user)

    return user

# ✔ DELETE
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.usr_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(user)
    db.commit()

    return {"message": "Usuário deletado com sucesso"}
