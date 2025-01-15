from datetime import datetime
from typing import  Optional, Union
from fastapi import Query
from pydantic import BaseModel

class BooksModel(BaseModel):
    pass

'''Users'''
class UserForAdmin(BaseModel):
    id: int
    login: str
    email: str
    created_at: datetime
    updated_at: datetime
    is_admin: bool
    books: Union[list[BooksModel], None] = Query(default=None)
    class Config:
        from_attributes = True 


class UserList(BaseModel):
    id: int
    login: str
    email: str
    created_at: datetime
    updated_at: datetime
    is_admin: bool
    boards: Optional[list[BooksModel]] = None
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
    class Config:
        from_attributes = True 


class Token(BaseModel):
    token: str


class UserId(BaseModel):
    id: int 


class UserUpdate(BaseModel):
    login: str
    password: str
    email: str
    is_admin: Optional[bool]
    class Config:
        from_attributes = True 


