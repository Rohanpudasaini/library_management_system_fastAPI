from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column
from sqlalchemy import Select, String, DateTime, BigInteger, Integer, ForeignKey, Boolean
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from database.database_connection import session, try_session_commit
from fastapi import HTTPException
import utils.constant_messages as constant_messages
from auth.auth import verify_password


class Base(DeclarativeBase):
    """Base class that inherit from DeclarativeBase of SQLAlchemy"""
    pass


# Assocication table schema of member and book
class MemberBook(Base):
    __tablename__ = 'member_book'
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column('user_id', Integer, ForeignKey('users.id'))
    book_id = mapped_column('book_id', String, ForeignKey('books.isbn_number'))


# Assocication table schema of member and magazine
class MemberMagazine(Base):
    __tablename__ = 'member_magazine'
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'))
    magazine_id = mapped_column(String, ForeignKey('magazines.issn_number'))

class RolePermission(Base):
    __tablename__ = 'role_permission'
    id = mapped_column(Integer,primary_key=True)
    role_id = mapped_column(Integer, ForeignKey('roles.id'))
    permission_id = mapped_column(Integer, ForeignKey('permissions.id'))


class Role(Base):
    __tablename__ = 'roles'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=True)
    users = relationship('User', back_populates='roles')
    # permission_id = mapped_column(Integer, ForeignKey('permissions.id'))
    permission_id = relationship('Permission', back_populates='role_id',secondary='role_permission', lazy='dynamic')
    
    @classmethod
    def get_role_permissions(cls,role_id):
        return session.scalars(Select(cls.permission_id).where(cls.id==role_id)).all()
    
    @classmethod
    def role_got_permission(cls,permission_name:str, role_id:int):
        permission_id = Permission.get_permission_id(permission_name)
        is_permitted = session.scalar(
            Select(RolePermission).where(
                RolePermission.role_id==role_id,
                RolePermission.permission_id == permission_id
                ))
        # return session.scalar(Select(cls.id).where(cls.name==permission_name))
        return is_permitted

class Permission(Base):
    __tablename__ = 'permissions'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=True)
    # role_id = mapped_column(Integer,ForeignKey('roles.id')) 
    role_id = relationship('Role', back_populates='permission_id', secondary='role_permission', lazy='dynamic')
    
    @classmethod
    def get_permission_id(cls,permission_name:str):
        return session.scalar(Select(cls.id).where(cls.name==permission_name))


class User(Base):
    __tablename__ = 'users'
    id = mapped_column(Integer(), primary_key=True)
    username = mapped_column(String(50), nullable=False, unique=True)
    email = mapped_column(String(50), nullable=False, unique=True)
    password = mapped_column(String, nullable=False, deferred=True)
    date_created = mapped_column(DateTime(), default=datetime.utcnow().date())
    expiry_date = mapped_column(
        DateTime(), default=datetime.utcnow().date() + timedelta(days=60))
    address = mapped_column(String(200), nullable=False)
    phone_number = mapped_column(BigInteger())
    fine = mapped_column(Integer, default=0)
    book_id = relationship(
        'Book', secondary='member_book', back_populates='user_id')
    magazine_id = relationship(
        'Magazine', secondary='member_magazine', back_populates='user_id')
    record = relationship('Record', backref='user')
    role_id = mapped_column(Integer, ForeignKey(
        'roles.id'), nullable=True, default=4)
    roles = relationship('Role', back_populates='users')

    def get_all_user(self, page, all, limit):
        if all:
            statement = Select(User).where(User.role_id >= 2)
            users = session.execute(statement).all()
        else:
            statement = Select(User).offset((page-1)*limit).limit(limit)
            users = session.execute(statement)
        users = [user[0] for user in users]
        return users

    def get_all_librarian(self, page, all, limit):
        if all:
            statement = Select(User).where(User.role_id == 1)
            users = session.execute(statement).all()
        else:
            statement = Select(User).offset((page-1)*limit).limit(limit)
            users = session.execute(statement)
        users = [user[0] for user in users]
        return users

    # Get only borrowed books or magazine

    def get_all_borrowed(self, username):
        userFound = self.get_from_username(username)
        book = []
        magazine = []
        if userFound.book_id:
            book = [book.title for book in userFound.book_id]

        if userFound.magazine_id:
            magazine = [magazine.title for magazine in userFound.magazine_id]
        if book == [] and magazine == []:
            return "No Book Borrowed"
        return {
            "Book": book,
            "Magazine": magazine
        }

    def get_from_username(self, username):
        """
        Give back the database instance of the user object
        from username
        """
        user_object = session.scalar(Select(User).where(User.username==username))
        if not user_object:
            raise HTTPException(status_code=404,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.REQUEST_NOT_FOUND,
                                        "error_message": constant_messages.request_not_found("user", "username")
                                    }
                                })
        return user_object

    def get_username_from_email(self, email):
        """
        Give back the username of user from username
        """
        user_object = session.query(User).where(
            User.email == email).one_or_none()
        if not user_object:
            raise HTTPException(status_code=404,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.REQUEST_NOT_FOUND,
                                        "error_message": constant_messages.request_not_found("user", "username")
                                    }
                                })
        return user_object.username

    def validate_user(self, email: str, password: str):
        """
        Simply Validate if a librarian with given email and password exsist
        Return Librarian object or None
        """
        selected_user = session.query(User).where(
            User.email == email,
        ).one_or_none()
        if selected_user:
            verified = verify_password(password, selected_user.password)
            if verified:
                return selected_user
        raise HTTPException(
            status_code=401,
            detail={
                'Error': constant_messages.UNAUTHORIZED_MESSAGE
            }
        )

    def add(self, username, email, address, phone_number, password, role_id = None):
        if not role_id:
            session.add(User(
                username=username,
                email=email,
                address=address,
                password=password,
                phone_number=phone_number
            ))
        else:
            session.add(User(
                username=username,
                email=email,
                address=address,
                password=password,
                phone_number=phone_number,
                role_id = role_id
            ))
        try:
            session.commit()
            return "User Added Sucessfully"
        except IntegrityError:
            session.rollback()
            # Same User Already Exsist
            raise HTTPException(status_code=400,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.BAD_REQUEST,
                                        "error_message": constant_messages.bad_request("User", "username or email")
                                    }
                                })

    def borrow_book(self, username, isbn_number, days=15):
        """
        Add book with given isbn number to a user with given username
        """
        book_to_add = session.query(Book).where(
            Book.isbn_number == isbn_number).one_or_none()
        if not book_to_add:
            raise HTTPException(status_code=404,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.REQUEST_NOT_FOUND,
                                        "error_message": constant_messages.request_not_found(
                                            "book",
                                            "ISBN number"
                                        )
                                    }
                                })

        user_object = self.get_from_username(username)

        user_object.book_id += [book_to_add]
        book_to_add.available_number -= 1
        user_already_exsist = session.query(Record).where(
            Record.book_id == book_to_add.isbn_number,
            Record.member_id == user_object.id,
            Record.returned == False
        ).count()
        if not user_already_exsist and book_to_add.available_number > 0:
            book_record = Record(
                user=user_object, book=book_to_add,
                genre=book_to_add.genre, issued_date=datetime.utcnow().date(),
                expected_return_date=(
                    datetime.utcnow().date() + timedelta(days=days))
            )
            session.add(book_record)
            try_session_commit(session)
        elif book_to_add.available_number == 0:
            raise HTTPException(status_code=409,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.INSUFFICIENT_RESOURCES,
                                        "error_message": constant_messages.insufficient_resources(
                                            "book"
                                        )
                                    }
                                })

        else:
            raise HTTPException(status_code=400,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.BAD_REQUEST,
                                        "error_message": constant_messages.bad_request(
                                            "book",
                                            "isbn",
                                            True
                                        )
                                    }
                                })

    def return_book(self, username, isbn_number):
        """
        Return book with given isbn number from a user with given username
        """
        book_to_return = session.query(Book).where(
            Book.isbn_number == isbn_number).one_or_none()
        # Invalid ISBN ERROR
        if not book_to_return:
            raise HTTPException(status_code=404,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.REQUEST_NOT_FOUND,
                                        "error_message": constant_messages.request_not_found(
                                            "book",
                                            "ISBN number")
                                    }
                                })
        user_object = self.get_from_username(username)

        # Get Unreturned books
        got_record = session.query(Record).where(
            Record.member_id == user_object.id,
            Record.book_id == isbn_number,
            Record.returned == False
        ).one_or_none()
        fine = 0

        if got_record:
            books_record = got_record

            # Check if the expected return date is 3 days before, if yes no fine is calculated
            if books_record.expected_return_date.date() < datetime.utcnow().date():
                extra_days = (datetime.utcnow().date() -
                              books_record.expected_return_date.date()).days

                # For each days after 3 days, fine is calculated as Rs 3 per day
                if extra_days > 3:
                    fine = extra_days * 3

            # sucessfull return, increased the available number
            # Also marked the book returned in Record
            book_to_return.available_number += 1
            books_record.returned = True
            books_record.returned_date = datetime.utcnow().date()

            # Delete the record from association table.
            session.query(MemberBook).filter(
                MemberBook.book_id == isbn_number,
                MemberBook.user_id == user_object.id
            ).delete()
            try_session_commit(session)
            return fine
        else:
            raise HTTPException(status_code=404,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.REQUEST_NOT_FOUND,
                                        "error_message": constant_messages.request_not_found(
                                            "username have issued books",
                                            "ISBN number"
                                        )
                                    }

                                })

    def return_magazine(self, username, issn_number):
        """
        User return magazine with given issn number from a user with given username

        Returns -> fine:int or None
        """

        magazine_to_return = session.query(Magazine).where(
            Magazine.issn_number == issn_number).one_or_none()

        if not magazine_to_return:
            raise HTTPException(status_code=404,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.REQUEST_NOT_FOUND,
                                        "error_message": constant_messages.request_not_found(
                                            "magazine", "ISSN number"
                                        )
                                    }
                                })

        # Check if username exsist
        user_object = self.get_from_username(username)

        # Check if record exsist
        got_record = session.query(Record).where(
            Record.member_id == user_object.id,
            Record.magazine_id == issn_number,
            Record.returned == False
        ).one_or_none()
        fine = 0
        if got_record:
            magazine_record = got_record

            # Check if the expected returned date is expired
            if magazine_record.expected_return_date.date() < datetime.utcnow().date():

                extra_days = (magazine_record.expected_return_date.date(
                ) - datetime.utcnow().date()).days

                # if magazine is't returned after 3 days of expected date
                # Calculate fine as Rs3 per day
                if extra_days > 3:
                    fine = extra_days * 3

            # Magazine Sucessfully returned
            # Increase available number and marked returned
            magazine_to_return.available_number += 1
            magazine_record.returned = True
            magazine_record.returned_date = datetime.utcnow().date()

            # Delete the record from association table
            session.query(MemberMagazine).filter(
                MemberMagazine.magazine_id == issn_number,
                MemberMagazine.user_id == user_object.id
            ).delete()
            try_session_commit(session)
            return fine
        else:
            raise HTTPException(status_code=404,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.REQUEST_NOT_FOUND,
                                        "error_message": constant_messages.request_not_found(
                                            "username have issued magazine", "ISSN number"
                                        )
                                    }
                                })

    def borrow_magazine(self, username, issn_number, days=15):
        """
        Add magazine with given issn number to a user with given username
        """
        magazine_to_add = session.query(Magazine).where(
            Magazine.issn_number == issn_number).one_or_none()
        if not magazine_to_add:
            raise HTTPException(status_code=404,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.REQUEST_NOT_FOUND,
                                        "error_message": constant_messages.request_not_found(
                                            "magazine",
                                            "ISSN number"
                                        )
                                    }
                                })
        # Check if user exsist and add the magazine to that user
        user_object = self.get_from_username(username)
        user_object.magazine_id += [magazine_to_add]

        # Check record if the magazine is already issued to same member
        user_already_exsist = session.query(Record).where(
            Record.magazine_id == magazine_to_add.issn_number,
            Record.member_id == user_object.id,
            Record.returned == False
        ).count()

        if not user_already_exsist and magazine_to_add.available_number > 0:
            magazine_to_add.available_number -= 1
            magazine_record = Record(
                user=user_object,
                magazine=magazine_to_add,
                genre=magazine_to_add.genre,
                issued_date=datetime.utcnow().date(),
                expected_return_date=(
                    datetime.utcnow().date() + timedelta(days=days))
            )
            session.add(magazine_record)
            try_session_commit(session)
        elif magazine_to_add.available_number == 0:
            raise HTTPException(status_code=409,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.INSUFFICIENT_RESOURCES,
                                        "error_message": constant_messages.insufficient_resources(
                                            "magazine"
                                        )
                                    }
                                })
        else:
            raise HTTPException(status_code=400,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.BAD_REQUEST,
                                        "error_message": constant_messages.bad_request(
                                            "magazine",
                                            "ISSN number",
                                            True
                                        )
                                    }
                                })


# Table schema of publisher
class Publisher(Base):
    __tablename__ = 'publishers'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(50), nullable=False, unique=True)
    address = mapped_column(String(200))
    phone_number = mapped_column(BigInteger())
    books = relationship('Book', backref='publisher')
    magazine = relationship('Magazine', backref='publisher')

    def get_all(self, page, all, limit):
        # return session.query(Publisher).all()
        if all:
            statement = Select(Publisher)
            publisher_list = session.execute(statement).all()
        else:
            statement = Select(Publisher).offset((page-1)*limit).limit(limit)
            publisher_list = session.execute(statement)
        publisher_list = [publisher_obj[0] for publisher_obj in publisher_list]
        return publisher_list

    def get_from_id(self, id):
        """
        Get a database instance of publisher object with given id
        Return publisher object or None
        """
        return session.query(Publisher).where(Publisher.id == id).one_or_none()

    def add(self, name, phone_number, address):
        session.add(Publisher(name=name, address=address,
                    phone_number=phone_number))
        try:
            session.commit()
            return "Publisher Added Sucessfully"

        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.BAD_REQUEST,
                                        "error_message": constant_messages.bad_request("Publisher", "publisher name")
                                    }
                                })


# Table schema of Book
class Book(Base):
    __tablename__ = 'books'
    isbn_number = mapped_column(String(15), nullable=False,
                         unique=True, primary_key=True, autoincrement=False)
    title = mapped_column(String(100), nullable=False)
    author = mapped_column(String(20), nullable=False, default='Folklore')
    price = mapped_column(Integer(), nullable=False)
    user_id = relationship('User', secondary='member_book', back_populates='book_id')
    genre_id = mapped_column(Integer(), ForeignKey('genre.id'))
    publisher_id = mapped_column(Integer, ForeignKey('publishers.id'))
    available_number = mapped_column(Integer, default=0)
    record = relationship('Record', backref='book')


    def get_all(self, all, page, limit):
        if all:
            statement = Select(Book)
            books = session.execute(statement).all()
        else:
            statement = Select(Book).offset((page-1)*limit).limit(limit)
            books = session.execute(statement)

        books = [book[0] for book in books]
        if books:
            return books
        raise HTTPException(status_code=204,
                            detail={
                                "error": {
                                    "error_type": constant_messages.NO_CONTENT,
                                    "error_message": constant_messages.NO_CONTENT_MESSAGE
                                }
                            })

    def get_from_id(self, isbn):
        """
        Get a database instance of book object with given isbn number
        Return book object or None
        """
        return session.query(Book).where(Book.isbn_number == str(isbn)).one_or_none()

    def add(self, isbn, author, title, price, genre_id, publisher_id, available_number):
        session.add(Book(
            isbn_number=isbn,
            author=author,
            price=price,
            title=title,
            genre_id=genre_id,
            publisher_id=publisher_id,
            available_number=available_number
        ))

        try:
            session.commit()
            return "Book Added Sucessfully"
        except IntegrityError as e:
            # print(e)
            session.rollback()
            # return "The Same Book Already exsist"
            raise HTTPException(status_code=400,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.BAD_REQUEST,
                                        "error_message": constant_messages.bad_request("book", "ISBN number")
                                    }
                                })


# Table schema of Magazine
class Magazine(Base):
    __tablename__ = 'magazines'
    issn_number = mapped_column(String(15), nullable=False,
                         unique=True, primary_key=True, autoincrement=False)
    title = mapped_column(String(100), nullable=False)
    editor = mapped_column(String(20), nullable=False, default='Folklore')
    price = mapped_column(Integer(), nullable=False)
    user_id = relationship(
        'User', secondary='member_magazine', back_populates='magazine_id')
    genre_id = mapped_column(Integer(), ForeignKey('genre.id'))
    publisher_id = mapped_column(Integer, ForeignKey('publishers.id'))
    available_number = mapped_column(Integer, default=0)
    record = relationship('Record', backref='magazine')

    def get_all(self, page, all, limit):
        if all:
            statement = Select(Magazine)
            magazines = session.execute(statement).all()
        else:
            statement = Select(Magazine).offset((page-1)*limit).limit(limit)
            magazines = session.execute(statement)
        magazines = [magazine[0] for magazine in magazines]
        if magazines:
            return magazines
        raise HTTPException(status_code=204,
                            detail={
                                "error": {
                                    "error_type":    constant_messages.NO_CONTENT,
                                    "error_message": constant_messages.NO_CONTENT_MESSAGE,
                                }
                            })

    def get_from_id(self, issn):
        """
        Get a database instance of magazine object with given issn number
        Return magazine object or None
        """
        return session.query(Magazine).where(Magazine.issn_number == str(issn)).one_or_none()

    def add(self, issn, editor, title, price, genre_id, publisher_id, available_number):
        session.add(Magazine(
            issn_number=issn,
            editor=editor,
            price=price,
            title=title,
            genre_id=genre_id,
            publisher_id=publisher_id,
            available_number=available_number
        ))

        try:
            session.commit()
            return "Magazine Added Sucessfully"
        except IntegrityError as e:
            # print(e)
            session.rollback()
            # return "The Same Magazine Already exsist"
            raise HTTPException(status_code=400,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.BAD_REQUEST,
                                        "error_message": constant_messages.bad_request("Magazine", "ISSN number")
                                    }
                                })


# Table schema of Genre
class Genre(Base):
    __tablename__ = 'genre'
    id = mapped_column(Integer(), primary_key=True)
    name = mapped_column(String(50), nullable=False, unique=True)
    books = relationship('Book', backref='genre')
    magazine = relationship('Magazine', backref='genre')
    record = relationship('Record', backref='genre')

    def get_all(self, page, all, limit):
        # return session.query(Genre).all()
        if all:
            statement = Select(Genre)
            genre_list = session.execute(statement).all()
        else:
            statement = Select(Genre).offset((page-1)*limit).limit(limit)
            genre_list = session.execute(statement)
        genre_list = [genre_obj[0] for genre_obj in genre_list]
        return genre_list

    def get_from_id(self, id):
        """
        Get a database instance of genre object with given id
        Return genre object or None
        """
        return session.query(Genre).where(Genre.id == id).one_or_none()

    def add(self, name):
        session.add(Genre(name=name))
        try:
            session.commit()
            return "Genre Added Sucessfully"
        except IntegrityError:
            session.rollback()
            # return "Same Genre Already Exsist"
            raise HTTPException(status_code=400,
                                detail={
                                    "error": {
                                        "error_type": constant_messages.BAD_REQUEST,
                                        "error_message": constant_messages.bad_request("Genre", "name")
                                    }
                                })


# Table schema for Record
class Record(Base):
    __tablename__ = 'records'
    id = mapped_column(Integer(), primary_key=True)
    member_id = mapped_column(Integer, ForeignKey('users.id'))
    book_id = mapped_column(String, ForeignKey('books.isbn_number'))
    magazine_id = mapped_column(String, ForeignKey('magazines.issn_number'))
    genre_id = mapped_column(Integer, ForeignKey('genre.id'))
    issued_date = mapped_column(DateTime(), default=datetime.utcnow().date())
    returned_date = mapped_column(DateTime(), default=datetime.utcnow().date())
    expected_return_date = mapped_column(DateTime(), default=(
        datetime.utcnow().date() + timedelta(days=15)))
    returned = mapped_column(Boolean, default=False)
