from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends
import error_constant
from models import Book, Magazine, User, Publisher, Genre, Librarian
from pydantic import BaseModel, EmailStr, Field, StrictStr
from auth.jwt_handler import decodRefreshJWT, encodeAccessJWT, generateToken
from auth.jwt_bearer import JwtBearer


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

book = Book()
magazine = Magazine()
publisher = Publisher()
genre = Genre()
user = User()
librarian = Librarian()


class BookItem(BaseModel):
    title: str
    author: str
    isbn: Annotated[StrictStr, Field(
        min_length=13,
        max_length=13,
        description="The ISBN number must be of 13 digit",
    )]
    price: Annotated[int, Field(
        gt=0,
        description="The price of the book must be greater than 0")]
    genre_id: Annotated[int, Field(
        gt=0,
        description="The Genre id must be greater than 0",
    )]
    publisher_id: Annotated[int, Field(
        gt=0,
        description="The Publisher id must be greater than 0",
    )]

    available_number: Annotated[int, Field(
        ge=0,
        description="The Book count must be greater than or equal 0",
    )]


class BorrowBookObject(BaseModel):
    username: str
    isbn: Annotated[StrictStr, Field(
        min_length=13,
        max_length=13,
        description="The ISBN number must be of 13 digit",
    )]
    days: int = 15


class ReturnBookObject(BaseModel):
    username: str
    isbn: Annotated[StrictStr, Field(
        min_length=13,
        max_length=13,
        description="The ISBN number must be of 13 digit",
    )]


class BorrowMagazineObject(BaseModel):
    username: str
    issn: Annotated[StrictStr, Field(
        min_length=8,
        max_length=8,
        description="The ISSN number must be of 8 digit",
    )]
    days: int = 15


class ReturnMagazineObject(BaseModel):
    username: str
    issn: Annotated[StrictStr, Field(
        min_length=8,
        max_length=8,
        description="The ISSN number must be of 8 digit",
    )]


class MagazineItem(BaseModel):
    editor: str
    title: str

    issn: Annotated[StrictStr, Field(
        min_length=8,
        max_length=8,
        description="The ISSN number must be of 8 digit",
    )]

    genre_id: Annotated[int, Field(
        gt=0,
        description="The Genre id must be greater than 0",
    )]
    publisher_id: Annotated[int, Field(
        gt=0,
        description="The Publisher id must be greater than 0",
    )]

    available_number: Annotated[int, Field(
        ge=0,
        description="The Magazine count must be greater than or equal 0",
    )]

    price: Annotated[int, Field(
        gt=0,
        description="The price of the book must be greater than 0")]


class PublisherItem(BaseModel):
    name: str
    phone_number: Annotated[int | None, Field(
        ge=1111111111, le=9999999999)] = None
    address: str | None = None


class LibrarianLogin(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)
    
    model_config = {
        "json_schema_extra" : {
            'examples':[
                {
                  "email": "admin@lms.com",
                  "password": "admin",
                }
            ]
        },
    }


class GenreItem(BaseModel):
    name: str


class UserItem(BaseModel):
    username: str
    email: str
    address: str
    phone_number: Annotated[int, Field(ge=1111111111, le=9999999999)]


@app.get('/', tags=['Home'])
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
    page:int|None=1, 
    all:bool|None=None, 
    limit:int|None=3
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
                'error_message': error_constant.request_not_found("publisher","ID"),
                }
        }
    )


@app.post(
    '/publisher',
    dependencies=[Depends(JwtBearer())],
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
    page:int|None=1, 
    all:bool|None=None, 
    limit:int|None=3
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
                'error_message': error_constant.request_not_found("genre","id"),
            }
        }
    )


@app.post('/genre', status_code=201, dependencies=[Depends(JwtBearer())], tags=['Genre'])
async def add_genre(genreItem: GenreItem):
    return {
        'result': genre.add(
            genreItem.name,
        )
    }


@app.get('/book', tags=['Book'])
async def list_books(
    page:int|None=1, 
    all:bool|None=None, 
    limit:int|None=3
    ):
    return {
        'Books': book.get_all(page=page,limit=limit,all=all)
    }
    
# @app.get('/book', tags=['Book'])
# async def list_books(numbers:int|None=None,all:bool|None=None):
#     return {
#         'Books': book.get_all(numbers,all)
#     }


@app.post('/book', status_code=201, dependencies=[Depends(JwtBearer())], tags=['Book'])
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
                'error_message': error_constant.request_not_found("publisher","ID"),
            }})
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type': error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("genre","ID"),
                }})


@app.get('/book/{isbn}', tags=['Book'])
async def get_book(isbn: str):
    if len(isbn) != 13:
        raise HTTPException(
            status_code=400,
            detail={'error': {
                'error_type': error_constant.INVALID_REQUEST,
                'error_message': error_constant.invalid_length("ISBN number",13)
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
                'error_message': error_constant.request_not_found("book","ISBN number")
                }})


@app.get('/magazine', tags=['Magazine'])
async def list_magazines(
    page:int|None=1, 
    all:bool|None=None, 
    limit:int|None=3
):
    return {
        'Magazines': magazine.get_all(page, all, limit)
    }


@app.post('/magazine', status_code=201, dependencies=[Depends(JwtBearer())], tags=['Magazine'])
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
                'error_message': error_constant.request_not_found("publisher","id")
            }})
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type':    error_constant.REQUEST_NOT_FOUND,
                'error_message': error_constant.request_not_found("genre","id")
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
                'error_message': error_constant.request_not_found("Magazine","ISSN number")
                }})


@app.get('/user', dependencies=[Depends(JwtBearer())], tags=['User'])
async def list_users(
    page:int|None=1, 
    all:bool|None=None, 
    limit:int|None=3
):
    return {
        'Users': user.get_all(page=page, all=all, limit=limit)
    }


@app.get('/user/borrowed', dependencies=[Depends(JwtBearer())], tags=['User'])
async def borrowed_items(username: str):
    return {
        "Username": username,
        'Borrowed': user.get_all_borrowed(username)

    }


@app.post('/user/borrow_book', dependencies=[Depends(JwtBearer())], tags=['User'])
async def user_borrow_book(borrowObject: BorrowBookObject):
    librarian.user_add_book(borrowObject.username, borrowObject.isbn)
    return {
        "Sucess": "Book Borrowed Sucessfully"
    }


@app.post('/user/borrow_magazine', dependencies=[Depends(JwtBearer())], tags=['User'])
async def user_borrow_magazine(borrowObject: BorrowMagazineObject):
    librarian.user_add_magazine(borrowObject.username, borrowObject.issn)
    return {
        "Sucess": "Magazine Borrowed Sucessfully"
    }


@app.post('/user/return_magazine', dependencies=[Depends(JwtBearer())], tags=['User'])
async def user_return_magazine(returnObject: ReturnMagazineObject):
    fine = librarian.user_return_magazine(
        returnObject.username, returnObject.issn)
    if fine:
        return {
            "Fine Remaning": {
                "Fine Ammount": fine,
                "Message": f"{returnObject.username} have {fine} rs remaning"
            }
        }
    return "Magazine Returned Sucessfully"


@app.post('/user/return_book', dependencies=[Depends(JwtBearer())], tags=['User'])
async def user_return_book(returnObject: ReturnBookObject):
    fine = librarian.user_return_book(returnObject.username, returnObject.isbn)
    if fine:
        return {
            "Fine Remaning": {
                "Fine Ammount": fine,
                "Message": f"{returnObject.username} have {fine} rs remaning"
            }
        }
    return "Book Returned Sucessfully"


@app.get('/user/{username}', dependencies=[Depends(JwtBearer())], tags=['User'])
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
                'error_message': error_constant.request_not_found("user",'usernaem')
            }
        }
    )


@app.post('/user', status_code=201, dependencies=[Depends(JwtBearer())], tags=['User'])
async def add_user(userItem: UserItem):
    return user.add(
        userItem.username,
        userItem.email,
        userItem.address,
        userItem.phone_number
    )


@app.get('/librarian', tags=['Librarian'])
async def list_librarians():
    return {
        'Users': librarian.get_all()
    }


@app.post('/login', tags=['Librarian'])
async def librarian_login(login_schema: LibrarianLogin):
    valid = librarian.validate_librarian(
        login_schema.email, login_schema.password)
    if valid:
        # token = encodeAccessJWT(login_schema.password)
        token = generateToken(login_schema.email)
        token.update({'email': login_schema.email})
        return token
    else:
        raise HTTPException(
            status_code=401,
            detail={
                'Error': {
                    'error_type': error_constant.UNAUTHORIZED,
                    'error_message': error_constant.UNAUTHORIZED_MESSAGE
                }
            }
        )


@app.get('/refresh', tags=['Librarian'])
async def get_new_accessToken(refreshToken: str):
    token = decodRefreshJWT(refreshToken)
    # return token
    if token:
        return {
            'access_token': encodeAccessJWT(token["userID"]),
            'userID': token["userID"]
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
