import os
import smtplib
from email.message import EmailMessage
from utils.main_message import html_message

EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')

def send_mail(email_to_send_to:str):
    message = EmailMessage()
    message['Subject'] = "Welcome to Library Management System"
    message['From'] = EMAIL
    message['To'] = email_to_send_to
    name = 'Rohan'
    message.set_content("welcome to the library management system, Your email is sucessfully verified.")
    message.add_alternative(html_message, subtype='html')


    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login(EMAIL,PASSWORD)
        smtp.send_message(message)