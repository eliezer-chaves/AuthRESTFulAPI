from passlib.context import CryptContext
import bcrypt
import hashlib
import base64
from logging_config import logger


pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password):
    try:
        # Codificar a senha para bytes
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        
        # Se você precisa armazenar como string, pode decodificar de volta
        # Mas normalmente bcrypt armazena como bytes ou string codificada
        return hashed.decode('utf-8')  # Converte bytes para string
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise

def verify_password(plain_password, hashed_password):
    try:
        # Certificar-se que ambos estão em bytes para verificação
        plain_bytes = plain_password.encode('utf-8')
        
        # Se hashed_password é string, converter para bytes
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
            
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False