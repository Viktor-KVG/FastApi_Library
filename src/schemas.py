from datetime import date, datetime
from typing import  Optional, Union, List
from fastapi import Query
from pydantic import BaseModel, Field, validator

'''Author'''
class AuthorsModel(BaseModel):
    id: int
    name: str
    biography: str
    date_of_birth: date 

    class Config:
        from_attributes = True


class CreateAuthorsModel(BaseModel):
    name: str
    biography: str
    date_of_birth: date

    @validator('name')
    def validate_name(cls, value):
        if not value:
            raise ValueError("The 'name' field cannot be empty.")
        if len(value) > 120:
            raise ValueError("The 'name' field must be no more than 120 characters long.")
        return value

    @validator('biography')
    def validate_biography(cls, value):
        if len(value) > 800:
            raise ValueError("The 'biography' field must contain no more than 800 characters.")
        return value
    
    class Config:
        from_attributes = True  


class AuthorId(BaseModel):
    id: int 

    class Config:
        from_attributes = True              


class SearchAuthorsModel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True 


'''Book'''
class BooksModel(BaseModel):
    id: int
    title: str
    description: str
    creator_id: int
    genre: str
    quantity: int
    authors: List['AuthorsModel'] = []

    class Config:
        from_attributes = True
        allow_population_by_field_name = True


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

    @validator('title')
    def validate_title(cls, value):
        if not value:
            raise ValueError("The 'title' field cannot be empty.")
        if len(value) > 120:
            raise ValueError("The 'title' field must be no more than 120 characters long.")
        return value
    
    @validator('description')
    def validate_description(cls, value):
        if len(value) > 500:
            raise ValueError("The 'description' field must contain no more than 500 characters.")
        return value
    
    @validator('genre')
    def validate_genre(cls, value):
        if len(value) > 120:
            raise ValueError("The 'genre' field must contain no more than 120 characters.")
        return value
    
    @validator('quantity')
    def validate_quantity(cls, value):
        if value < 0:
            raise ValueError("The 'quantity' field must be a non-negative integer.")
        return value
    
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


class SearchBooksList(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None

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

    @validator('login')
    def validate_login(cls, value):
        if not value:
            raise ValueError("The 'login' field cannot be empty.")
        if len(value) > 60:
            raise ValueError("The 'login' field must be no more than 60 characters long.")
        return value

    @validator('password')
    def validate_password(cls, value):
        if not value:
            raise ValueError("The 'password' field cannot be empty.")
        if len(value) > 60:
            raise ValueError("The 'password' field must be no more than 60 characters long.")
        return value
    
    @validator('email')
    def validate_email(cls, value):
        if not value:
            raise ValueError("The 'email' field cannot be empty.")
        if len(value) > 160:
            raise ValueError("The 'email' field must be no more than 160 characters long.")
        return value

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


