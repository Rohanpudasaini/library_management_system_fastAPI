from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, String, DateTime, BigInteger, Integer, ForeignKey, Boolean
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from database_connection import session

class Base(DeclarativeBase):
    pass


class MemberBook(Base):
    __tablename__ = 'member_book'
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    book_id = Column('book_id', String, ForeignKey('books.isbn_number'))

    
class MemberMagazine(Base):
    __tablename__ = 'member_magazine'
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    magazine_id = Column('magazine_id', String,
                         ForeignKey('magazines.issn_number'))
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False)
    date_created = Column(DateTime(), default=datetime.utcnow().date())
    expiry_date = Column(
        DateTime(), default=datetime.utcnow().date() + timedelta(days=60))
    address = Column(String(200), nullable=False)
    phone_number = Column(BigInteger())
    fine = Column(Integer, default=0)
    book_id = relationship(
        'Book', secondary='member_book', back_populates='user_id')
    magazine_id = relationship(
        'Magazine', secondary='member_magazine', back_populates='user_id')
    record = relationship('Record', backref='user')
    
    
    def get_all(self):
        return session.query(User).all()
    
    def get_from_username(self, username):
        return session.query(User).where(User.username==username).one_or_none()
    
  
class Publisher(Base):
    __tablename__ = 'publishers'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    address = Column(String(200))
    phone_number = Column(BigInteger())
    books = relationship('Book', backref='publisher')
    magazine = relationship('Magazine', backref='publisher')
    
    def get_all(self):
        return session.query(Publisher).all()
    
    def get_from_id(self, id):
        return session.query(Publisher).where(Publisher.id == id).one_or_none()


class Book(Base):
    __tablename__ = 'books'
    isbn_number = Column(String(15), nullable=False,
                         unique=True, primary_key=True, autoincrement=False)
    title = Column(String(100), nullable=False)
    author = Column(String(20), nullable=False, default='Folklore')
    price = Column(Integer(), nullable=False)
    user_id = relationship(
        'User', secondary='member_book', back_populates='book_id')
    genre_id = Column(Integer(), ForeignKey('genre.id'))
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
    available_number = Column(Integer, default=0)
    record = relationship('Record', backref='book')
    
    
    def get_all(self):
        books = session.query(Book).all()
        return books
    
    def get_from_id(self, isbn):
        return session.query(Book).where(Book.isbn_number == str(isbn)).one_or_none()
    
    def add(self,isbn,author,title,price,genre_id,publisher_id,available_number):
        session.add(Book(
                isbn_number=isbn,
                author=author,
                price=price,
                title=title,
                genre_id = genre_id,
                publisher_id= publisher_id,
                available_number = available_number
                ))

        try:
            session.commit()
            return "Book Added Sucessfully"
        except IntegrityError as e:
            # print(e)
            session.rollback()
            return "The Same Book Already exsist"
        
    
    
    

class Magazine(Base):
    __tablename__ = 'magazines'
    issn_number = Column(String(15), nullable=False,
                         unique=True, primary_key=True, autoincrement=False)
    title = Column(String(100), nullable=False)
    editor = Column(String(20), nullable=False, default='Folklore')
    price = Column(Integer(), nullable=False)
    user_id = relationship(
        'User', secondary='member_magazine', back_populates='magazine_id')
    genre_id = Column(Integer(), ForeignKey('genre.id'))
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
    available_number = Column(Integer, default=0)
    record = relationship('Record', backref='magazine')
    
    def get_all(self):
        return session.query(Magazine).all()
    
    def get_from_id(self, issn):
        return session.query(Magazine).where(Magazine.issn_number == str(issn)).one_or_none()
    

class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    books = relationship('Book', backref='genre')
    magazine = relationship('Magazine', backref='genre')
    record = relationship('Record', backref='genre')
    
    
    def get_all(self):
        return session.query(Genre).all()
    
    def get_from_id(self, id):
        return session.query(Genre).where(Genre.id == id).one_or_none()
    
class Librarian(Base):
    __tablename__ = 'librarians'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    address = Column(String(200), nullable=False)
    phone_number = Column(BigInteger())




class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer(), primary_key=True)
    member_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(String, ForeignKey('books.isbn_number'))
    magazine_id = Column(String, ForeignKey('magazines.issn_number'))
    genre_id = Column(Integer, ForeignKey('genre.id'))
    issued_date = Column(DateTime(), default=datetime.utcnow().date())
    returned_date = Column(DateTime(), default=datetime.utcnow().date())
    expected_return_date = Column(DateTime(), default=(
        datetime.utcnow().date() + timedelta(days=15)))
    returned = Column(Boolean, default=False)