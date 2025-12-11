# schemas/user.py
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Annotated, Optional
from datetime import datetime

# Tipos validados
PasswordStr = Annotated[str, Field(min_length=8)]

# Campos base (compartilhados entre create/update/response)
class UserBase(BaseModel):
    usr_first_name: str
    usr_last_name: str
    usr_email: EmailStr
    usr_phone: str | None = None
    
class UserLogin(BaseModel):
    usr_email: EmailStr
    usr_password: PasswordStr

# Dados recebidos ao criar usuário (inclui senha)
class UserCreate(UserBase):
    usr_password: PasswordStr
    
    @field_validator('usr_password')
    @classmethod
    def validate_password_length(cls, v):
        # Verifica se a senha não excede 72 bytes quando codificada
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Senha muito longa (máximo 72 bytes em UTF-8)')
        return v

# Dados recebidos ao atualizar usuário (tudo opcional)
class UserUpdate(BaseModel):
    usr_first_name: Optional[str] = None
    usr_last_name: Optional[str] = None
    usr_email: Optional[EmailStr] = None
    usr_password: Optional[PasswordStr] = None
    
    @field_validator('usr_password')
    @classmethod
    def validate_password_length(cls, v):
        if v is not None and len(v.encode('utf-8')) > 72:
            raise ValueError('Senha muito longa (máximo 72 bytes em UTF-8)')
        return v

class UserEmail(BaseModel):
    usr_email: EmailStr

class UserResponse(UserBase):
    usr_id: int
    
    model_config = ConfigDict(from_attributes=True)  