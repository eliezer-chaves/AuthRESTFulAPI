from sqlalchemy import Column, Integer, String, DateTime, TIMESTAMP
from database import Base

class EmailRateLimit(Base):
    __tablename__ = "erl_email_rate_limits"
    
    erl_id = Column(Integer, primary_key=True, index=True)
    erl_email = Column(String(255), index=True, nullable=False)
    erl_ip_address = Column(String(45), index=True, nullable=True)
    erl_attempts = Column(Integer, default=1)
    erl_first_attempt_at = Column(TIMESTAMP(timezone=True), nullable=False)
    erl_last_attempt_at = Column(TIMESTAMP(timezone=True), nullable=False)
    erl_blocked_until = Column(TIMESTAMP(timezone=True), nullable=False)
    erl_created_at = Column(TIMESTAMP(timezone=True), nullable=False)
