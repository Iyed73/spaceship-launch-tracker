from smtplib import SMTPException
from flask import current_app
from app import mail


def send_email(message):
    try:
        mail.send(message)
    except (SMTPException, OSError):
        current_app.logger.exception("Failed to send email to %s", message.recipients)
        return False
    return True
