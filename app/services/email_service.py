import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL")

    if not smtp_host:
        raise ValueError("SMTP_HOST is not set in the .env file")

    if not smtp_username:
        raise ValueError("SMTP_USERNAME is not set in the .env file")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD is not set in the .env file")

    if not smtp_from_email:
        raise ValueError("SMTP_FROM_EMAIL is not set in the .env file")

    message = EmailMessage()
    message["From"] = smtp_from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)