from fastapi_mail import FastMail, MessageSchema, MessageType
from core.config.email_config import mail_config
from core.utils.template_renderer import load_template
import os
from logging_config import logger
from fastapi_mail.errors import ConnectionErrors

fastmail = FastMail(mail_config)

front_url = os.getenv("FRONT_URL")
api_url = os.getenv("API_URL")

app_name = os.getenv("APP_NAME")
expiration_minutes = int(os.getenv("MAIL_EXPIRATION_CODE_MINUTRES"))

async def send_reset_code_email(email: str, code: str, user_name: str):
    try:
        html_body = load_template("reset_password.html", {
            "app_name": app_name,
            "user_name": user_name,
            "reset_code": code,
            "expiration_minutes": expiration_minutes,
            "current_year": 2025
        })

        message = MessageSchema(
            subject=f"{app_name} - Reset code",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html
        )

        #logger.info("📨 Iniciando envio SMTP...")
        await fastmail.send_message(message)
        #logger.info("✅ EMAIL ENVIADO — sem erro no SMTP")

    except ConnectionErrors as smtp_error:
        logger.error(f"❌ SMTP ERROR: {smtp_error}")
        raise

    except Exception as e:
        logger.error(f"❌ GENERAL EMAIL ERROR: {e}")
        raise
    
async def send_confirmation_email(email: str, user_name: str, email_token: str):
    try:
        html_body = load_template("confirm_account.html", {
            "app_name": app_name,
            "user_name": user_name,
            "email_token": f'{front_url}/auth/verified-email/?token={email_token}',
            "ect_expires_at": expiration_minutes,
        })

        message = MessageSchema(
            subject=f"{app_name} - Confirm Your Email",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html
        )

        #logger.info("📨 Iniciando envio SMTP...")
        await fastmail.send_message(message)
        #logger.info("✅ EMAIL ENVIADO — sem erro no SMTP")

    except ConnectionErrors as smtp_error:
        logger.error(f"❌ SMTP ERROR: {smtp_error}")
        raise

    except Exception as e:
        logger.error(f"❌ GENERAL EMAIL ERROR: {e}")
        raise