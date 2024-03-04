from typing import Annotated
from fastapi import FastAPI, HTTPException, Query
from models import Book, Magazine, User, Publisher, Genre
app = FastAPI()
    
book = Book()
magazine = Magazine()
publisher = Publisher()
genre = Genre()
user = User()

@app.get('/')
async def home_route():
    return {
        'Message': 'Welcome to the library management system using FastAPI Please find all the available path below',
        'path': {
            'user': '/user/',
            'book': '/book/',
            'magazine': '/magazine/',
            'publisher': '/publisher/',
            'genre': '/genre/',
        }    
    }

# @app.get('/book')
# async def book_route(isbn: Annotated[str | None, Query(min_length=13,max_length=13)] = None):
#     if isbn:
#         return {
#             'book':book.get_from_id(isbn)}
#     return {
#         'Books': book.get_all_book()    
#     }
    
@app.get('/book')
async def list_books():
        return {
        'Books': book.get_all()    
    }
        
@app.get('/book/{isbn}')
async def get_book(isbn:str):
    if len(isbn) != 13:
        raise HTTPException(
            status_code=400,
            detail={'error':{
                'error_type': 'Invalid Request',
                'error_message': 'The ISBN number must be 13 characer'
            }})
        
    bookFound = book.get_from_id(isbn)
    if bookFound:
        return {
            'book': bookFound
        }
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type': 'Request Not Found',
                'error_message': f'The Book with ISBN number {isbn} not found'
            }})
    
    
    
# @app.get('/magazine')
# async def magazine_route(issn: Annotated[str | None, Query(min_length=8,max_length=8)] = None):
    
#     if issn:
#         return {
#             'magazine': magazine.get_from_id(issn)
#         }
    
#     return {
#         'Magazines': magazine.get_all()    
#     }

@app.get('/magazine')
async def list_magazines():
        return {
        'Magazines': magazine.get_all()    
    }
        
@app.get('/magazine/{issn}')
async def get_magazine(issn:str):
    if len(issn) != 8:
        raise HTTPException(
            status_code=400,
            detail={'error':{
                'error_type': 'Invalid Request',
                'error_message': 'The ISSN number must be 8 characer'
            }})

        
    magazineFound = magazine.get_from_id(issn)
    if magazineFound:
        return {
            'Magazine': magazineFound
        }
    raise HTTPException(
        status_code=404,
        detail={'error': {
                'error_type': 'Request Not Found',
                'error_message': f'The Magazine with ISSN number {issn} not found'
            }})

    
@app.get('/publisher')
async def list_publishers(id:int|None= None):
    
    if not id:
        return {
            'Publishers': publisher.get_all()    
        }
    return{
        'Publisher': publisher.get_from_id(id)
    }
    
@app.get('/genre')
async def list_genre(id:int|None= None):
    if not id:
        return {
            'Genre': genre.get_all()    
        }
    return {
        'Genre': genre.get_from_id(id)
    }
    
@app.get('/user')
async def list_users(username:str|None = None):
    
    if not username:
        return {
            'Users': user.get_all()    
        }
    return {
        'User': user.get_from_username(username)
    }