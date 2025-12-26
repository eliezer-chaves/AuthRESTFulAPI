from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Annotated, Optional

PasswordStr = Annotated[str, Field(min_length=8)]


class UserBase(BaseModel):
    usr_first_name: str
    usr_last_name: str
    usr_email: EmailStr
    usr_phone: str | None = None


class UserLogin(BaseModel):
    usr_email: EmailStr
    usr_password: PasswordStr


class UserCreate(UserBase):
    usr_password: PasswordStr

    @field_validator("usr_password")
    @classmethod
    def validate_password_length(cls, v: str):
        if len(v.encode("utf-8")) > 72:
            raise ValueError({
                "type": "password_too_long",
                "title": "Password Too Long",
                "message": "The password must not exceed 72 bytes when encoded in UTF-8."
            })
        return v


class UserUpdate(BaseModel):
    usr_first_name: Optional[str] = None
    usr_last_name: Optional[str] = None
    usr_email: Optional[EmailStr] = None
    usr_password: Optional[PasswordStr] = None

    @field_validator("usr_password")
    @classmethod
    def validate_password_length(cls, v: Optional[str]):
        if v is not None and len(v.encode("utf-8")) > 72:
            raise ValueError({
                "type": "password_too_long",
                "title": "Password Too Long",
                "message": "The password must not exceed 72 bytes when encoded in UTF-8."
            })
        return v


class UserEmail(BaseModel):
    usr_email: EmailStr


class UserResponse(UserBase):
    usr_id: int

    model_config = ConfigDict(from_attributes=True)
