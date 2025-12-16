from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy.orm import relationship
from models.password_reset_code import PasswordResetCode

class User(Base):
    __tablename__ = "usr_users"

    usr_id = Column(Integer, primary_key=True, index=True)
    usr_first_name = Column(String(100), nullable=False)
    usr_last_name = Column(String(100), nullable=False)
    usr_phone = Column(String(20), nullable=True)
    usr_email = Column(String(80), unique=True, nullable=False)
    usr_password = Column(String(255), nullable=False)
    usr_email_verified = Column(Boolean, nullable=False, server_default="false")
    usr_user_active = Column(Boolean, nullable=False, server_default="false")

    usr_reset_codes = relationship(PasswordResetCode, back_populates="usr_user")
