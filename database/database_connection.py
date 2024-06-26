from fastapi import HTTPException
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from decouple import config
import utils.constant_messages as constant_messages

# Load info from .env
host = config('host')
database = config('database')
user = config('user')
password = config('password')

# Create a connection url using SQL Alchemy's URL class
url = URL.create(
    database=database,
    username=user,
    password=password,
    host=host,
    drivername="postgresql"
)

# create a engine with above created url
engine = create_engine(url, echo=False)

try:
    engine.connect().close()

except OperationalError:
    print("No valid credentials, please ensure the presence of .env file")
# Create a session
# TODO: make the session with context manager
session = Session(bind=engine)

#  Get session and try to commit
# If error occurs, rollback and show generic HTTPException


def try_session_commit(session):
    try:
        session.commit()
    except IntegrityError as e:
        print(e._message())
        session.rollback()
        raise HTTPException(status_code=500,
                            detail={
                                "error": {
                                    "error_type": constant_messages.INTERNAL_ERROR,
                                    "error_message": constant_messages.INTERNAL_ERROR_MESSAGE
                                }
                            })
