import secrets
import hashlib

def generate_email_token() -> str:
    return secrets.token_urlsafe(32)


def make_hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def validate_token(token_from_url: str, token_hash_from_db: str) -> bool:
    return make_hash_token(token_from_url) == token_hash_from_db
