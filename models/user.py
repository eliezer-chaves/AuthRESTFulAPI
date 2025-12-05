from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "usr_users"

    usr_id = Column(Integer, primary_key=True, index=True)
    usr_first_name = Column(String(100), nullable=False)
    usr_last_name = Column(String(100), nullable=False)
    usr_email = Column(String(80), unique=True, nullable=False)
    usr_password = Column(String(255), nullable=False)
