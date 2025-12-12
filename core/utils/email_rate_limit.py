from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request
from datetime import datetime, timedelta
from models.email_rate_limit import EmailRateLimit
import os

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def check_rate_limit(
    email: str,
    request: Request,
    db: Session
) -> Optional[dict]:
    """Rate limit usando datetimes naive (UTC)."""
    

    # Config
    rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    if not rate_limit_enabled:
        return None

    max_attempts = int(os.getenv("RATE_LIMIT_MAX_ATTEMPTS", "3"))
    window_hours = int(os.getenv("RATE_LIMIT_WINDOW_HOURS", "1"))

    # Agora sem timezone
    now = datetime.utcnow()
    ip_address = get_client_ip(request)

    # Busca ou cria registro
    rate_limit = db.query(EmailRateLimit).filter(
        EmailRateLimit.erl_email == email
    ).first()

    if not rate_limit:
        rate_limit = EmailRateLimit(
            erl_email=email,
            erl_ip_address=ip_address,
            erl_attempts=1,
            erl_first_attempt_at=now,
            erl_last_attempt_at=now
        )
        db.add(rate_limit)
        db.commit()
        return None

    # Converte para naive caso MySQL retorne de forma inconsistente
    first = rate_limit.erl_first_attempt_at.replace(tzinfo=None) if rate_limit.erl_first_attempt_at.tzinfo else rate_limit.erl_first_attempt_at
    blocked_until = (
        rate_limit.erl_blocked_until.replace(tzinfo=None)
        if rate_limit.erl_blocked_until and rate_limit.erl_blocked_until.tzinfo
        else rate_limit.erl_blocked_until
    )

    # Está bloqueado?
    if blocked_until and blocked_until > now:
        remaining_seconds = int((blocked_until - now).total_seconds())
        return {
            "blocked": True,
            "blocked_until": blocked_until.isoformat(),
            "remaining_seconds": remaining_seconds,
            "remaining_minutes": remaining_seconds // 60,
            "attempts": rate_limit.erl_attempts
        }

    # Janela expirou?
    if now - first > timedelta(hours=window_hours):
        rate_limit.erl_attempts = 1
        rate_limit.erl_first_attempt_at = now
        rate_limit.erl_last_attempt_at = now
        rate_limit.erl_blocked_until = None
        db.commit()
        return None

    # Incrementa tentativas
    rate_limit.erl_attempts += 1
    rate_limit.erl_last_attempt_at = now
    rate_limit.erl_ip_address = ip_address

    # Excedeu limite?
    if rate_limit.erl_attempts > max_attempts:
        block_until = now + timedelta(hours=window_hours)
        rate_limit.erl_blocked_until = block_until
        db.commit()

        remaining_seconds = int((block_until - now).total_seconds())
        return {
            "blocked": True,
            "blocked_until": block_until.isoformat(),
            "remaining_seconds": remaining_seconds,
            "remaining_minutes": remaining_seconds // 60,
            "attempts": rate_limit.erl_attempts
        }

    # Ainda dentro do limite
    db.commit()
    return {
        "blocked": False,
        "attempts": rate_limit.erl_attempts,
        "max_attempts": max_attempts,
        "remaining_attempts": max_attempts - rate_limit.erl_attempts
    }
