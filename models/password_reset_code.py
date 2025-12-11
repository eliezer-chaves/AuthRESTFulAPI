from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class PasswordResetCode(Base):
    __tablename__ = "psc_password_reset_codes"

    psc_id = Column(Integer, primary_key=True, index=True)
    psc_user_id = Column(Integer, ForeignKey("usr_users.usr_id"), nullable=False)
    psc_code = Column(String(6), nullable=False)
    psc_expires_at = Column(DateTime(timezone=True), nullable=False)
    psc_used_at = Column(DateTime(timezone=True), nullable=True)
    psc_created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))


    usr_user = relationship("User", back_populates="usr_reset_codes")
