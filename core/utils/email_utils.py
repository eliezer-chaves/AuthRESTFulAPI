import secrets
import random
import time
from pathlib import Path

def generate_email_token() -> str:
    return secrets.token_urlsafe(32)

def generate_reset_code():
    random.seed(time.time_ns())
    return str(random.randint(100000, 999999))

def mask_email(email: str) -> str:
    name, domain = email.split("@")
    
    if len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[:2] + "*" * (len(name) - 2)
    
    return f"{masked_name}@{domain}"


def load_template(template_name: str, variables: dict) -> str:
    base_path = Path(__file__).resolve().parent.parent / "templates"
    file_path = base_path / template_name

    if not file_path.exists():
        raise FileNotFoundError(f"❌ Template não encontrado: {file_path}")

    template = file_path.read_text(encoding="utf-8")

    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        if placeholder not in template:
            print(f"⚠️ Aviso: placeholder {placeholder} não encontrado no template.")
        template = template.replace(placeholder, str(value))

    return template
