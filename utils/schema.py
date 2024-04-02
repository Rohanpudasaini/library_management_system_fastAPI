from pydantic import BaseModel, EmailStr, Field, StrictStr
from typing import Annotated

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
    username: str | None = None
    isbn: Annotated[StrictStr, Field(
        min_length=13,
        max_length=13,
        description="The ISBN number must be of 13 digit",
    )]
    days: int = 15


class ReturnBookObject(BaseModel):
    username: str | None = None
    isbn: Annotated[StrictStr, Field(
        min_length=13,
        max_length=13,
        description="The ISBN number must be of 13 digit",
    )]


class BorrowMagazineObject(BaseModel):
    username: str | None = None
    issn: Annotated[StrictStr, Field(
        min_length=8,
        max_length=8,
        description="The ISSN number must be of 8 digit",
    )]
    days: int = 15


class ReturnMagazineObject(BaseModel):
    username: str | None = None
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


class LoginScheme(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)

    model_config = {
        "json_schema_extra": {
            'examples': [
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
    password: str
    phone_number: Annotated[int, Field(ge=1111111111, le=9999999999)]
    role_id:int|None =None

class EmailModel(BaseModel):
    email:EmailStr