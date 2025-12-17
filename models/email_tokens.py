from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, TIMESTAMP
from database import Base
from sqlalchemy.orm import relationship

class Token(Base):
    __tablename__ = "ect_email_confirmation_token"

    ect_id = Column(Integer, primary_key=True, index=True)
    ect_user_id = Column(Integer, ForeignKey("usr_users.usr_id", ondelete="CASCADE"), nullable=False)
    ect_token = Column(String(255), nullable=False, index=True)
    ect_expires_at = Column(TIMESTAMP(timezone=True), nullable=False)

    ect_user = relationship("User", back_populates="usr_email_token")
