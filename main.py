from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import Select
from auth import auth
from auth.permission_checker import PermissionChecker, ContainPermission
import utils.constant_messages as constant_messages
from models import Book, Magazine, User, Publisher, Genre, Role
from utils.schema import *
from utils import send_mail
# from utils.helper_function import log_request, log_response, LogMiddleware
from utils.helper_function import  LogMiddleware
from utils.helper_function import token_in_header
from database.database_connection import session

# from fastapi.security import HTTPBearer
# token_in_header = HTTPBearer()


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

app.add_middleware(LogMiddleware, exclude_paths=['/docs', '/openapi.json', '/login','/refresh'])

# @app.middleware('http')
# async def log_middleware(request: Request, call_next):
#     if request.url.path != '/docs':
#         await log_request(request)
#         response = await call_next(request)
#         if request.url.path != '/openapi.json':
#             response = await log_response(response)
#     else:
#         response = await call_next(request)
#     return response


book = Book()
magazine = Magazine()
publisher = Publisher()
genre = Genre()
user = User()
role = Role()


def is_verified(token:dict = Depends(token_in_header)):
    email = token['user_identifier']
    username = user.get_username_from_email(email)
    user_object = user.get_from_username(username)
    if 'user:verified' in [permission.name for permission in (session.scalars(user_object.roles.permission_id).all()) ]:
        return "You are already verified"
    return token


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
                'error_type': constant_messages.REQUEST_NOT_FOUND,
                'error_message': constant_messages.request_not_found("publisher", "ID"),
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
                'error_type': constant_messages.REQUEST_NOT_FOUND,
                'error_message': constant_messages.request_not_found("genre", "id"),
            }
        }
    )


@app.post('/genre', status_code=201, dependencies=[Depends(PermissionChecker(['user:verified']))], tags=['Genre'])
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


@app.post('/book', status_code=201, dependencies=[Depends(PermissionChecker(['user:verified']))], tags=['Book'])
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
                'error_type': constant_messages.REQUEST_NOT_FOUND,
                'error_message': constant_messages.request_not_found("publisher", "ID"),
            }})
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type': constant_messages.REQUEST_NOT_FOUND,
                'error_message': constant_messages.request_not_found("genre", "ID"),
                }})


@app.get('/book/{isbn}', tags=['Book'])
async def get_book(isbn: str):
    if len(isbn) != 13:
        raise HTTPException(
            status_code=400,
            detail={'error': {
                'error_type': constant_messages.INVALID_REQUEST,
                'error_message': constant_messages.invalid_length("ISBN number", 13)
            }})

    bookFound = book.get_from_id(isbn)
    if bookFound:
        return {
            'book': bookFound
        }
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type': constant_messages.REQUEST_NOT_FOUND,
                'error_message': constant_messages.request_not_found("book", "ISBN number")
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


@app.post('/magazine', status_code=201, dependencies=[Depends(PermissionChecker(['user:verified']))], tags=['Magazine'])
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
                'error_type':    constant_messages.REQUEST_NOT_FOUND,
                'error_message': constant_messages.request_not_found("publisher", "id")
            }})
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type':    constant_messages.REQUEST_NOT_FOUND,
                'error_message': constant_messages.request_not_found("genre", "id")
                }})


@app.get('/magazine/{issn}', tags=['Magazine'])
async def get_magazine(issn: str):
    if len(issn) != 8:
        raise HTTPException(
            status_code=400,
            detail={'error': {
                'error_type': constant_messages.INVALID_REQUEST,
                'error_message': constant_messages.invalid_length("ISSN number", 8)
            }})

    magazineFound = magazine.get_from_id(issn)
    if magazineFound:
        return {
            'Magazine': magazineFound
        }
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type':    constant_messages.REQUEST_NOT_FOUND,
                'error_message': constant_messages.request_not_found("Magazine", "ISSN number")
                }})


@app.get('/user', dependencies=[Depends(PermissionChecker(['user:verified']))], tags=['User'])
async def list_users(
    page: int | None = 1,
    all: bool | None = None,
    limit: int | None = 3
):
    return {
        'Users': user.get_all_user(page=page, all=all, limit=limit)
    }


@app.get('/user/borrowed', dependencies=[Depends(PermissionChecker(['user:all']))], tags=['User'])
async def borrowed_items(username: str):
    return {
        "Username": username,
        'Borrowed': user.get_all_borrowed(username)

    }


@app.post('/user/borrow_book', tags=['User'])
async def borrow_book(borrowObject: BorrowBookObject, token=Depends(token_in_header)):
    if token['role'] != 'user':
        if borrowObject.username:
            user.borrow_book(borrowObject.username, borrowObject.isbn)
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    'error': constant_messages.BAD_REQUEST,
                    'error_message': "No Username in provided, admins must provide username to whom the book should be issued to "
                }
            )
    else:
        username = user.get_username_from_email(token['user_identifier'])
        user.borrow_book(username, borrowObject.isbn)

    return {
        "Sucess": "Book Borrowed Sucessfully"
    }


@app.post('/user/borrow_magazine', tags=['User'])
async def borrow_magazine(borrowObject: BorrowMagazineObject, token=Depends(token_in_header)):
    if token['role'] != 'user':
        if borrowObject.username:
            user.borrow_magazine(borrowObject.username, borrowObject.issn)
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    'error': constant_messages.BAD_REQUEST,
                    'error_message': "No Username in provided, admins must provide username to whom the magazine should be issued to "
                }
            )
    else:
        username = user.get_username_from_email(token['user_identifier'])
        user.borrow_magazine(username, borrowObject.issn)
    return {
        "Sucess": "Magazine Borrowed Sucessfully"
    }


@app.post('/user/return_magazine', tags=['User'])
async def return_magazine(returnObject: ReturnMagazineObject, token=Depends(token_in_header)):
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
                    'error': constant_messages.BAD_REQUEST,
                    'error_message': "No Username in provided, admins must provide username of user returning magazine"
                }
            )
    else:
        username = user.get_username_from_email(token['user_identifier'])
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
async def return_book(returnObject: ReturnBookObject, token=Depends(token_in_header)):
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
                    'error': constant_messages.BAD_REQUEST,
                    'error_message': "No Username in provided, admins must provide username of user returning book"
                }
            )
    else:
        username = user.get_username_from_email(token['user_identifier'])
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


@app.get('/me', tags=['User'])
async def get_my_info(token=Depends(token_in_header)):
    # token = auth.decodAccessJWT(token.credentials)
    username = user.get_username_from_email(token['user_identifier'])
    user_details = user.get_from_username(username)
    return {
        'User': {
            'user_details': user_details
        }
    }


@app.get('/me/borrowed', tags=['User'])
async def borrowed_items(token = Depends(token_in_header)):
    # token = auth.decodAccessJWT(token.credentials)
    username = user.get_username_from_email(token['user_identifier'])
    return {
        "Username": username,
        'Borrowed': user.get_all_borrowed(username)

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
                'error_type':    constant_messages.REQUEST_NOT_FOUND,
                'error_message': constant_messages.request_not_found("user", 'usernaem')
            }
        }
    )



@app.post('/user', status_code=201, dependencies=[Depends(PermissionChecker(['user:verified']), use_cache=False)], tags=['User'])
async def add_user(userItem: UserItem, isAdmin:bool = Depends(ContainPermission(['admin:all']))):
    if not userItem.role_id:
        return user.add(
            userItem.username,
            userItem.email,
            userItem.address,
            userItem.phone_number,
            auth.hash_password(userItem.password)
        )
    elif isAdmin:
        return user.add(
        userItem.username,
        userItem.email,
        userItem.address,
        userItem.phone_number,
        auth.hash_password(userItem.password),
        userItem.role_id
        )
    else:
        raise HTTPException(
            status_code=403,
            detail="Only admin can add user with different role_id")


@app.get('/admin', tags=['User'], dependencies=[Depends(PermissionChecker(['admin:all']))])
async def list_admin():
    return {
        'Users': user.get_all_librarian()
    }


@app.post('/login', tags=['Authentication'])
async def login(login_schema: LoginScheme):
    valid_user = user.validate_user(login_schema.email, login_schema.password)
    token = auth.generate_JWT(login_schema.email, role=valid_user.role_id)
    return {
        'access_token': token[0],
        'refresh_token': token[1],
        'role': valid_user.role_id
    }


@app.post('/refresh', tags=['Authentication'])
async def get_new_accessToken(refreshToken:RefreshTokenModel):
    token = auth.decodRefreshJWT(refreshToken.token)
    if token:
        return {
            'access_token': token
        }
    raise HTTPException(
        status_code=401,
        detail={
            'Error': {
                'error_type': constant_messages.TOKEN_ERROR,
                'error_message': constant_messages.TOKEN_VERIFICATION_FAILED
            }
        }
    )


@app.post('/verify', tags=['Authentication'])
def verify_user(email:EmailModel, token:dict = Depends(is_verified)):
    if isinstance(token,dict):
        user_email = token['user_identifier']
        username = user.get_username_from_email(user_email)
        user_object = user.get_from_username(username)
        if user_object.email == email.email:
            role_id = session.scalar(Select(Role.id).where(Role.name == 'verified user'))
            user_object.role_id = role_id
            session.add(user_object)
            session.commit()
            send_mail.send_mail(email.email)
            return 'Verified Sucesfully, please login again to get updated token'
        raise HTTPException(
            status_code= 404,
            detail= "This email donot match with the email in our system."
        )
    else:
        return token


@app.get(
    '/role', 
    dependencies=[Depends(PermissionChecker(permissions_required=['user:verified']))],
    tags=['Authentication']
    )
def get_all_available_role():
    return session.scalars(Select(Role)).all()


@app.post(
    '/role', 
    dependencies=[Depends(PermissionChecker(permissions_required=['admin:all']))],
    tags=['Authentication'],
    status_code=201
    )
def add_role(roleModel:RoleModel):
    # print(roleModel.name, roleModel.permission)
    result = Role.add(roleModel.name, roleModel.permission)
    if not result:
        return {"sucess":"Sucessfully added role with provided permissions"}
    return {
        "Sucess": "Sucessfully added role but wasn't able to add following permission as they don't exsist",
        "Error": result
    }
    
@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal. Request again with teleport = true as query"})
    # return {"message": "Here's your interdimensional portal."}