from pydantic import BaseModel, Field, EmailStr
from typing import Annotated


# Tipos validados (Pydantic v2 recomendado)
PasswordStr = Annotated[str, Field(min_length=8)]


# Campos base (compartilhados entre create/update/response)
class UserBase(BaseModel):
    usr_first_name: str
    usr_last_name: str
    usr_email: EmailStr


# Dados recebidos ao criar usuário (inclui senha)
class UserCreate(UserBase):
    usr_password: PasswordStr


# Dados recebidos ao atualizar usuário (tudo opcional)
class UserUpdate(BaseModel):
    usr_first_name: str | None = None
    usr_last_name: str | None = None
    usr_email: EmailStr | None = None
    usr_password: PasswordStr | None = None


# Dados retornados para o cliente (não inclui senha)
class UserResponse(UserBase):
    usr_id: int

    class Config:
        from_attributes = True  # substitui orm_mode (Pydantic v1)
