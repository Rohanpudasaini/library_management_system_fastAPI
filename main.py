from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy import Select
from auth import auth
from auth.PermissionChecker import PermissionChecker
import error_constant
from models import Book, Magazine, User, Publisher, Genre, Role
from schema import *
from functions import log_request, log_response, token_in_header
from database_connection import session


description = """
Library Management API helps you do awesome stuff. 🚀

Please go to  `/` to know about ervery availabe route.
"""


app = FastAPI(
    title="LibraryManagementSystem",
    description=description,
    summary="All your library related stuff.",
    version="0.0.1",
    contact={
        "name": "Rohan Pudasaini",
        "url": "https://rohanpudasaini.com.np",
        "email": "admin@rohanpudasaini.com.np",
    },
)


@app.middleware('http')
async def log_middleware(request: Request, call_next):
    await log_request(request)
    response = await call_next(request)
    response = await log_response(response)
    return response


book = Book()
magazine = Magazine()
publisher = Publisher()
genre = Genre()
user = User()
role = Role()


def is_verified(token:dict = Depends(token_in_header)):
    email = token['user_id']
    username = user.get_username_from_email(email)
    user_object = user.get_from_username(username)
    if 'user:verified' in user_object.roles.permission:
        return "You are already verified"
    return token



def admin_only(payload=Depends(token_in_header)):
    if payload['role'] == 'admin':
        return 'Hello'
    raise HTTPException(
        status_code=401,
        detail={
            'error': "UNAUTHORIZED",
            'message': "You don't have access to view this endpoint"
        }
    )


@app.get(
    '/', 
    tags=['Home'], 
    dependencies=[Depends(PermissionChecker(['user:unverified']))])
async def home_route():
    return {
        'Message': 'Welcome to the library management system using \
FastAPI Please find all the available path below',
        'path': {
            'user': '/user/',
            'book': '/book/',
            'magazine': '/magazine/',
            'publisher': '/publisher/',
            'genre': '/genre/',
            'librarian': '/librarian'
        },
        'tips': 'please head to /docs to try the endpoint online or see the docs.'
    }


@app.get('/publisher', tags=['Publisher'])
async def list_publishers(
    page: int | None = 1,
    all: bool | None = None,
    limit: int | None = 3
):
    return {
        'Publishers': publisher.get_all(page=page, all=all, limit=limit)
    }


@app.get('/publisher/{publisherId}', tags=['Publisher'])
async def get_publisher(publisherId: int):
    publisherFound = publisher.get_from_id(publisherId)
    if publisherFound:
        return {
            'Publisher': publisherFound
        }
    raise HTTPException(
        status_code=404,
        detail={
            'Error': {
                'error_type': error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("publisher", "ID"),
            }
        }
    )


@app.post(
    '/publisher',
    dependencies=[Depends(PermissionChecker(['admin:all']))],
    tags=['Publisher'],
    status_code=201
)
async def add_publisher(publisherItem: PublisherItem):
    return {
        'result': publisher.add(
            publisherItem.name,
            publisherItem.phone_number,
            publisherItem.address
        )
    }


@app.get('/genre', tags=['Genre'])
async def list_genre(
    page: int | None = 1,
    all: bool | None = None,
    limit: int | None = 3
):
    return {
        'Genre': genre.get_all(page=page, all=all, limit=limit)
    }


@app.get('/genre/{genreId}', tags=['Genre'])
async def get_genre(genreId: int):
    publisherFound = genre.get_from_id(genreId)
    if publisherFound:
        return {
            'Publisher': publisherFound
        }
    raise HTTPException(
        status_code=404,
        detail={
            'Error': {
                'error_type': error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("genre", "id"),
            }
        }
    )


@app.post('/genre', status_code=201, dependencies=[Depends(admin_only)], tags=['Genre'])
async def add_genre(genreItem: GenreItem):
    return {
        'result': genre.add(
            genreItem.name,
        )
    }


@app.get('/book', tags=['Book'])
async def list_books(
    page: int | None = 1,
    all: bool | None = None,
    limit: int | None = 3
):
    return {
        'Books': book.get_all(page=page, limit=limit, all=all)
    }


@app.post('/book', status_code=201, dependencies=[Depends(admin_only)], tags=['Book'])
async def add_book(book_item: BookItem):
    if await get_genre(book_item.genre_id):
        if await get_publisher(book_item.publisher_id):
            return {
                'Result': book.add(
                    book_item.isbn,
                    book_item.author,
                    book_item.title,
                    book_item.price,
                    book_item.genre_id,
                    book_item.publisher_id,
                    book_item.available_number
                )}
        raise HTTPException(
            status_code=404,
            detail={'error': {
                'error_type': error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("publisher", "ID"),
            }})
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type': error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("genre", "ID"),
                }})


@app.get('/book/{isbn}', tags=['Book'])
async def get_book(isbn: str):
    if len(isbn) != 13:
        raise HTTPException(
            status_code=400,
            detail={'error': {
                'error_type': error_constant.INVALID_REQUEST,
                'error_message': error_constant.invalid_length("ISBN number", 13)
            }})

    bookFound = book.get_from_id(isbn)
    if bookFound:
        return {
            'book': bookFound
        }
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type': error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("book", "ISBN number")
                }})


@app.get('/magazine', tags=['Magazine'])
async def list_magazines(
    page: int | None = 1,
    all: bool | None = None,
    limit: int | None = 3
):
    return {
        'Magazines': magazine.get_all(page, all, limit)
    }


@app.post('/magazine', status_code=201, dependencies=[Depends(admin_only)], tags=['Magazine'])
async def add_magazine(magazine_item: MagazineItem):
    if await get_genre(magazine_item.genre_id):
        if await get_publisher(magazine_item.publisher_id):
            return {
                'Result': magazine.add(
                    magazine_item.issn,
                    magazine_item.editor,
                    magazine_item.title,
                    magazine_item.price,
                    magazine_item.genre_id,
                    magazine_item.publisher_id,
                    magazine_item.available_number
                )}
        raise HTTPException(
            status_code=404,
            detail={'error': {
                'error_type':    error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("publisher", "id")
            }})
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type':    error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("genre", "id")
                }})


@app.get('/magazine/{issn}', tags=['Magazine'])
async def get_magazine(issn: str):
    if len(issn) != 8:
        raise HTTPException(
            status_code=400,
            detail={'error': {
                'error_type': error_constant.INVALID_REQUEST,
                'error_message': error_constant.invalid_length("ISSN number", 8)
            }})

    magazineFound = magazine.get_from_id(issn)
    if magazineFound:
        return {
            'Magazine': magazineFound
        }
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type':    error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("Magazine", "ISSN number")
                }})


@app.get('/user', dependencies=[Depends(admin_only)], tags=['User'])
async def list_users(
    page: int | None = 1,
    all: bool | None = None,
    limit: int | None = 3
):
    return {
        'Users': user.get_all_user(page=page, all=all, limit=limit)
    }


@app.get('/user/borrowed', dependencies=[Depends(admin_only)], tags=['User'])
async def borrowed_items(username: str):
    return {
        "Username": username,
        'Borrowed': user.get_all_borrowed(username)

    }


@app.post('/user/borrow_book', tags=['User'])
async def user_borrow_book(borrowObject: BorrowBookObject, token=Depends(token_in_header)):
    if token['role'] != 'user':
        if borrowObject.username:
            user.borrow_book(borrowObject.username, borrowObject.isbn)
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    'error': error_constant.BAD_REQUEST,
                    'error_message': "No Username in provided, admins must provide username to whom the book should be issued to "
                }
            )
    else:
        username = user.get_username_from_email(token['user_id'])
        user.borrow_book(username, borrowObject.isbn)

    return {
        "Sucess": "Book Borrowed Sucessfully"
    }


@app.post('/user/borrow_magazine', tags=['User'])
async def user_borrow_magazine(borrowObject: BorrowMagazineObject, token=Depends(token_in_header)):
    if token['role'] != 'user':
        if borrowObject.username:
            user.borrow_magazine(borrowObject.username, borrowObject.issn)
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    'error': error_constant.BAD_REQUEST,
                    'error_message': "No Username in provided, admins must provide username to whom the magazine should be issued to "
                }
            )
    else:
        username = user.get_username_from_email(token['user_id'])
        user.borrow_magazine(username, borrowObject.issn)
    return {
        "Sucess": "Magazine Borrowed Sucessfully"
    }


@app.post('/user/return_magazine', tags=['User'])
async def user_return_magazine(returnObject: ReturnMagazineObject, token=Depends(token_in_header)):
    if token['role'] != 'user':
        if returnObject.username:
            fine = user.return_magazine(
                returnObject.username, returnObject.issn)
            if fine:
                return {"Sucess": "Sucesfully returned, but fine remaning",
                        "Fine Remaning": {
                            "Fine Ammount": fine,
                            "Message": f"{returnObject.username} have {fine} rs remaning"
                        }
                        }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    'error': error_constant.BAD_REQUEST,
                    'error_message': "No Username in provided, admins must provide username of user returning magazine"
                }
            )
    else:
        username = user.get_username_from_email(token['user_id'])
        fine = user.return_magazine(username, returnObject.issn)
        if fine:
            return {"Sucess": "Sucesfully returned, but fine remaning",
                    "Fine Remaning": {
                        "Fine Ammount": fine,
                        "Message": f"{returnObject.username} have {fine} rs remaning"
                    }
                    }

    return {"sucess": "Magazine Returned Sucessfully"}


@app.post('/user/return_book', tags=['User'])
async def user_return_book(returnObject: ReturnBookObject, token=Depends(token_in_header)):
    if token['role'] != 'user':
        if returnObject.username:
            fine = user.return_book(returnObject.username, returnObject.isbn)
            if fine:
                return {
                    "Sucess": "Sucesfully returned, but fine remaning",
                    "Fine Remaning": {
                        "Fine Ammount": fine,
                        "Message": f"{returnObject.username} have {fine} rs remaning"
                    }
                }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    'error': error_constant.BAD_REQUEST,
                    'error_message': "No Username in provided, admins must provide username of user returning book"
                }
            )
    else:
        username = user.get_username_from_email(token['user_id'])
        fine = user.return_book(username, returnObject.isbn)
        if fine:
            return {
                "Sucess": "Sucesfully returned, but fine remaning",
                "Fine Remaning": {
                    "Fine Ammount": fine,
                    "Message": f"{returnObject.username} have {fine} rs remaning"
                }
            }
    return {"Sucess": "Book Returned Sucessfully"}


@app.get('/me')
async def get_my_info(token=Depends(token_in_header)):
    username = user.get_username_from_email(token['user_id'])
    user_details = user.get_from_username(username)
    return {
        'User': {
            'user_details': user_details
        }
    }


@app.get('/user/{username}', dependencies=[Depends(PermissionChecker(['user:verified']))], tags=['User'])
async def get_user(username: str):
    userFound = user.get_from_username(username)
    if userFound:
        return {
            'User': {
                "user_details": userFound,

            }
        }
    raise HTTPException(
        status_code=404,
        detail={
            'Error': {
                'error_type':    error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("user", 'usernaem')
            }
        }
    )


@app.post('/user', status_code=201, dependencies=[Depends(admin_only)], tags=['User'])
async def add_user(userItem: UserItem):
    return user.add(
        userItem.username,
        userItem.email,
        userItem.address,
        userItem.phone_number,
        auth.hash_password(userItem.password)
    )


@app.get('/librarian', tags=['Librarian'], dependencies=[Depends(admin_only)])
async def list_librarians():
    return {
        'Users': user.get_all_librarian()
    }


@app.post('/login', tags=['Librarian'])
async def login(login_schema: LoginScheme):
    valid_user = user.validate_user(login_schema.email, login_schema.password)
    token = auth.generate_JWT(login_schema.email, role=valid_user.role_id)
    return {
        'access_token': token[0],
        'refresh_token': token[1],
        'role': valid_user.role_id
    }


@app.get('/refresh', tags=['Librarian'])
async def get_new_accessToken(refreshToken: str):
    token = auth.decodRefreshJWT(refreshToken)
    if token:
        return {
            'access_token': token
        }
    raise HTTPException(
        status_code=401,
        detail={
            'Error': {
                'error_type': error_constant.TOKEN_ERROR,
                'error_message': error_constant.TOKEN_VERIFICATION_FAILED
            }
        }
    )


@app.post('/verify')
def verify_user(email:EmailModel, token:dict = Depends(is_verified)):
    if isinstance(token,dict):
        user_email = token['user_id']
        username = user.get_username_from_email(user_email)
        user_object = user.get_from_username(username)
        if user_object.email == email.email:
            role_id = session.scalar(Select(Role.id).where(Role.name == 'verified user'))
            user_object.role_id = role_id
            session.add(user_object)
            session.commit()
            return 'Verified Sucesfully'
        raise HTTPException(
            status_code= 404,
            detail= "This email donot match with the email in our system."
        )
    else:
        return token
