import os
from sqlalchemy import text, create_engine, URL, inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from dotenv import load_dotenv
# from databse_connection.create_table_schema import create_database, Librarian, Magazine, \
    # MemberBooks, User, Books, Publisher, Record, MemberMagazine, try_session_commit, Genre
# from cli_components import error_assci

load_dotenv()

host = os.getenv('host')
database = os.getenv('database')
user = os.getenv('user')
password = os.getenv('password')


url = URL.create(
    database=database,
    username=user,
    password=password,
    host=host,
    drivername="postgresql"
)
engine = create_engine(url, echo=False)
session = Session(bind=engine)
