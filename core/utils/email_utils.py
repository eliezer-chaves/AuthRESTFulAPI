import secrets
import random
import time
from pathlib import Path
from logging_config import logger
from fastapi import HTTPException

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
    try:
        base_path = Path(__file__).resolve().parent.parent / "templates"
        file_path = base_path / template_name

        if not file_path.exists():
            logger.error(f"Template not found: {file_path}")
            raise HTTPException(
                status_code=500,
                detail={
                    "type": "email_template_not_found",
                    "title": "Email Template Not Found",
                    "message": "The email template required to send this message could not be found."
                }
            )

        template = file_path.read_text(encoding="utf-8")

        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder not in template:
                logger.warning(f"Placeholder not found in template: {placeholder}")

            template = template.replace(placeholder, str(value))

        return template

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Template processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "type": "email_template_processing_failed",
                "title": "Template Processing Failed",
                "message": "An unexpected error occurred while processing the email template."
            }
        )
