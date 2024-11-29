from flask_mail import Message
from app import mail, create_app
from config import DevelopmentConfig


app = create_app(DevelopmentConfig)
app.app_context().push()


def send_email_notification(recipient, content, subject):
    message = Message(recipients=[recipient], sender=app.config["APP_EMAIL"])
    message.html = content
    message.subject = subject
    mail.send(message)
