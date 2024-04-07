#!/usr/local/bin/python
from database.database_connection import session
from models import Magazine, Record, User, Book, Select
import datetime
from utils import send_mail

def get_all_expiring_record():
    now = datetime.datetime.now().date()
    expiring_records = session.execute(
        Select(
            Record.expected_return_date, 
            Record.book_id,Record.magazine_id, 
            Record.member_id
            ).where(
                Record.expected_return_date == (now + datetime.timedelta(3))
                )).all()
    # return expiring_records
    if expiring_records:
        for expiring_record in expiring_records:
            id_to_sent = expiring_record[3]
            user = session.scalar(Select(User).where(User.id==id_to_sent))
            user_email = user.email
            username = user.username
            if expiring_record[2]:
                object = "Magazine"
                name = session.scalar(Select(Magazine.title).where(Magazine.issn_number==expiring_record[2]))
            elif expiring_record[1]:
                object = "Book"
                name = session.scalar(Select(Book.title).where(Book.isbn_number==expiring_record[1]))
                
            send_mail.expiring_mail(user_email, username,name, object)
            print(f'Sent mail to {user_email}')


def get_all_expired_records():
    now = datetime.datetime.now().date()
    expired_records = session.execute(
        Select(
            Record.expected_return_date, 
            Record.book_id,Record.magazine_id, 
            Record.member_id
            ).where(
                Record.expected_return_date <= (now)
                )).all()
    # return expired_records
    if expired_records:
        for expired_record in expired_records:
            id_to_sent = expired_record[3]
            user = session.scalar(Select(User).where(User.id==id_to_sent))
            user_email = user.email
            username = user.username
            if expired_record[2]:
                object = "Magazine"
                name = session.scalar(Select(Magazine.title).where(Magazine.issn_number==expired_record[2]))
            elif expired_record[1]:
                object = "Book"
                name = session.scalar(Select(Book.title).where(Book.isbn_number==expired_record[1]))
            expired_date = str(expired_record[0].date())
            extra_days = (now - expired_record[0].date()).days
            fine = extra_days * 3
            send_mail.expired_mail(user_email, username,name, object,expired_date,fine)
            print(f'Sent mail to {user_email}')
            

get_all_expiring_record()
get_all_expired_records()