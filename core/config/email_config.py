from pydantic import BaseModel, EmailStr
from fastapi_mail import ConnectionConfig
import os

class MailSettings(BaseModel):
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

mail_settings = MailSettings(
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS") == "True",
)

mail_config = ConnectionConfig(
    MAIL_USERNAME=mail_settings.MAIL_USERNAME,
    MAIL_PASSWORD=mail_settings.MAIL_PASSWORD,
    MAIL_FROM=mail_settings.MAIL_FROM,
    MAIL_SERVER=mail_settings.MAIL_SERVER,
    MAIL_PORT=mail_settings.MAIL_PORT,
    MAIL_FROM_NAME=mail_settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=mail_settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=mail_settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)
