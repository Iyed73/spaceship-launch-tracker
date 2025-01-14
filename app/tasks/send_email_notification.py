from flask import current_app
from flask_mail import Message
from app import mail


def send_email_notification(recipient, content, subject):
    message = Message(recipients=[recipient], sender=current_app.config["APP_EMAIL"])
    message.html = content
    message.subject = subject
    mail.send(message)
