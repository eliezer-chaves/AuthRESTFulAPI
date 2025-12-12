from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime, timezone

class EmailRateLimit(Base):
    __tablename__ = "erl_email_rate_limits"
    
    erl_id = Column(Integer, primary_key=True, index=True)
    erl_email = Column(String(255), index=True, nullable=False)
    erl_ip_address = Column(String(45), index=True, nullable=True)
    erl_attempts = Column(Integer, default=1)
    erl_first_attempt_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    erl_last_attempt_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    erl_blocked_until = Column(DateTime(timezone=True), nullable=True)
    erl_created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
