from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from database import Base
from sqlalchemy.orm import relationship

class RefreshToken(Base):
    __tablename__ = "rft_refresh_tokens"

    rft_id = Column(Integer, primary_key=True, index=True)
    rft_user_id = Column(Integer, ForeignKey("usr_users.usr_id", ondelete="CASCADE"), nullable=False)
    rft_hash_token = Column(String(255), nullable=False, index=True)
    rft_expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    rft_revoked_at = Column(TIMESTAMP(timezone=True), nullable=True)
    rft_created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    rft_last_used_at = Column(TIMESTAMP(timezone=True), nullable=False)

    usr_user = relationship("User", back_populates="usr_refresh_tokens")