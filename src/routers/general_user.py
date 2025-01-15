"""
Общий файл для всех роутеров. Если возникнет необходимость, то его можно поделить на отдельные файлы по сгруппированным endpoint'ам
Например: routers/user.py, routers/board.py и т.д.
"""

from typing import Any, List, Optional
from fastapi.encoders import jsonable_encoder
from fastapi.responses import UJSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query,  status, HTTPException

import core.core_user
from src.database import session_factory, get_db
from src.schemas import (
    Token,
    UserId,
    UserLogin,
    UserCreate,
    UserCreateResponse,
    UserForAdmin,
    UserList,
    UserUpdate
)
import core
from src.auth import auth_jwt


api_router = APIRouter(
    prefix="/api",
    tags=["api_user"]
)


@api_router.post("/user", response_model=UserCreateResponse)   
def create_user(data: UserCreate):
    if core.core_user.is_user_exist(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Error in data entry, such user already exists'
        )
    else:
        user = core.register_user(data)
        return user


@api_router.post("/user/login_jwt", response_model=Token)
def user_login_jwt(data: UserLogin):
    func = auth_jwt.user_login(data)
    if func:
        return {'token': func}
    elif func == False:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal Server Error'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Authentication error, incorrect credentials'
        )



