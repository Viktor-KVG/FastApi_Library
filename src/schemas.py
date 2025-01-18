from datetime import date, datetime
from typing import  Optional, Union, List
from fastapi import Query
from pydantic import BaseModel, Field

'''Author'''
class AuthorsModel(BaseModel):
    id: int
    name: str
    biography: str
    date_of_birth: date  
    book: List['BooksModel'] = []
    class Config:

        from_attributes = True

class CreateAuthorsModel(BaseModel):
    name: str
    biography: str
    date_of_birth: date = Field(..., description="Дата рождения автора") 
    # book: List['BooksModel'] = []
    class Config:
        from_attributes = True  

class AuthorId(BaseModel):
    id: int 
    class Config:
        from_attributes = True              



'''Book'''
class BooksModel(BaseModel):
    id: int
    title: str
    description: str
    author_id: int
    genre: str
    quantity: int
    class Config:

        from_attributes = True


class BookListModel(BaseModel):
    title: Optional[str] = None

    class Config:
        from_attributes = True


class CreateBookModel(BaseModel):

    title: str
    description: str
    author_id: int
    genre: str
    quantity: int
    class Config:
        from_attributes = True


    class Config:
        from_attributes = True


class BookId(BaseModel):
    id: int 
    class Config:
        from_attributes = True    


class PutBook(BaseModel):
    title: str
    description: str
    author_id: int
    genre: str
    quantity: int
    class Config:
        from_attributes = True

'''Users'''
class UserForAdmin(BaseModel):
    id: int
    login: str
    email: str
    created_at: datetime
    updated_at: datetime
    is_admin: bool
    books: list[BooksModel] = []
    class Config:
        from_attributes = True 


class UserList(BaseModel):
    id: int
    login: str
    email: str
    created_at: datetime
    updated_at: datetime
    is_admin: bool
    books: list[BooksModel] = []
    class Config:
        from_attributes = True   


class UserLogin(BaseModel):
    login: str
    password: str
    class Config:
        from_attributes = True 


class UserCreate(BaseModel):
    login: str
    password: str
    email: str
    is_admin: Optional[bool] = False
    class Config:
        from_attributes = True 


class UserCreateResponse(BaseModel):
    id: int
    login: str
    email: str
    is_admin: bool
    token: str 
    class Config:
        from_attributes = True 


class Token(BaseModel):
    token: str


class TokenData(BaseModel):
    login: str | None = None
    class Config:
        from_attributes = True 


class UserInDB(UserForAdmin):
    hashed_password: str   


class UserId(BaseModel):
    id: int 


class UserUpdate(BaseModel):
    login: str
    password: str
    email: str
    is_admin: Optional[bool]
    class Config:
        from_attributes = True 


class SearchUsersList(BaseModel):
    id: Optional[int] = None
    login: Optional[str] = None
    email: Optional[str] = None   
    class Config:
        from_attributes = True         


