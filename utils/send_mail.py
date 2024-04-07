import os
import smtplib
from email.message import EmailMessage
from utils.main_message import get_verified_html, get_return_reminder_html, get_expiry_notification_html

EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')

async def send_verification_mail(email_to_send_to:str,username:str):
    message = EmailMessage()
    message['Subject'] = "Welcome to Library Management System"
    message['From'] = EMAIL
    message['To'] = email_to_send_to
    message.set_content("welcome to the library management system, Your email is sucessfully verified.")
    message.add_alternative(get_verified_html(username.title()), subtype='html')


    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login(EMAIL,PASSWORD)
        smtp.send_message(message)

def expiring_mail(email_to_send_to:str,username:str, name:str, object:str):
    message = EmailMessage()
    message['Subject'] = "Book Soon To Expire"
    message['From'] = EMAIL
    message['To'] = email_to_send_to
    message.set_content(f"This is a friendly reminder that your borrowed {object} {name} is due for return in 3 days.")
    message.add_alternative(get_return_reminder_html(username,name,object), subtype='html')


    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login(EMAIL,PASSWORD)
        smtp.send_message(message)


def expired_mail(email_to_send_to:str,username:str, name:str, object:str, expirary_date:str, fine:str):
    message = EmailMessage()
    message['Subject'] = "Book Expired"
    message['From'] = EMAIL
    message['To'] = email_to_send_to
    message.set_content(f"This is a friendly reminder that your borrowed {object} {name} have already expired at {expirary_date} and fine ammount of रु {fine} is due.")
    message.add_alternative(get_expiry_notification_html(username,name,object, expirary_date, fine), subtype='html')


    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login(EMAIL,PASSWORD)
        smtp.send_message(message)