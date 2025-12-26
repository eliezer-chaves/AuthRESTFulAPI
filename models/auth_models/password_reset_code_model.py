from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base


class PasswordResetCode(Base):
    __tablename__ = "psc_password_reset_codes"

    psc_id = Column(Integer, primary_key=True, index=True)
    psc_user_id = Column(Integer, ForeignKey("usr_users.usr_id",  ondelete="CASCADE"), nullable=False)
    psc_code = Column(String(6), nullable=False)
    psc_expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    psc_used_at = Column(TIMESTAMP(timezone=True), nullable=False)
    psc_created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    psc_reset_id = Column(String(36), unique=True, index=True, nullable=False)


    usr_user = relationship("User", back_populates="usr_reset_codes")
