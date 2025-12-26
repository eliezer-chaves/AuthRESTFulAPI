from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from core.config.email_config import mail_config
from core.utils.email_utils import *
import os
from logging_config import logger
from datetime import date

fastmail = FastMail(mail_config)

front_url = os.getenv("FRONT_URL")
api_url = os.getenv("API_URL")

app_name = os.getenv("APP_NAME")
expiration_minutes = int(os.getenv("SHORT_LIVED_TTL_MINUTES"))
today = date.today()
current_year = today.year

async def send_reset_code_email(email: str, code: str, user_name: str):
    try:
        html_body = load_template("reset_password.html", {
            "app_name": app_name,
            "user_name": user_name,
            "reset_code": code,
            "expiration_minutes": expiration_minutes,
            "current_year": current_year
        })

        message = MessageSchema(
            subject=f"{app_name} - Reset Code",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html
        )

        await fastmail.send_message(message)

    except ConnectionErrors as smtp_error:
        logger.error(f"SMTP ERROR: {smtp_error}")
        raise HTTPException(
            status_code=503,
            detail={
                "type": "email_service_unavailable",
                "title": "Email Service Unavailable",
                "message": "We could not send the reset email at this time. Please try again later."
            }
        )

    except Exception as e:
        logger.error(f"GENERAL EMAIL ERROR: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "type": "email_delivery_failed",
                "title": "Email Delivery Failed",
                "message": "An unexpected error occurred while sending the reset email."
            }
        )
  
async def send_confirmation_email(email: str, user_name: str, email_token: str):
    try:
        html_body = load_template("confirm_account.html", {
            "app_name": app_name,
            "user_name": user_name,
            "email_token": f"{front_url}/auth/verified-email/?token={email_token}",
            "ect_expires_at": expiration_minutes,
            "current_year": current_year
        })

        message = MessageSchema(
            subject=f"{app_name} - Confirm Your Email",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html
        )

        await fastmail.send_message(message)

    except ConnectionErrors as smtp_error:
        logger.error(f"SMTP ERROR: {smtp_error}")
        raise HTTPException(
            status_code=503,
            detail={
                "type": "email_service_unavailable",
                "title": "Email Service Unavailable",
                "message": "We could not send the confirmation email at this time. Please try again later."
            }
        )

    except Exception as e:
        logger.error(f"GENERAL EMAIL ERROR: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "type": "email_delivery_failed",
                "title": "Email Delivery Failed",
                "message": "An unexpected error occurred while sending the confirmation email."
            }
        )
