"""
Общий файл для всех роутеров. Если возникнет необходимость, то его можно поделить на отдельные файлы по сгруппированным endpoint'ам
Например: routers/user.py, routers/board.py и т.д.
"""


import logging
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt import JwtAccessBearer
from src.settings import SECRET_KEY

from src.auth.auth_jwt import get_current_user, authenticate_user
from src.models import UserModel
from src.database import get_db
from src.schemas import (
    SearchUsersList,
    Token,
    UserCreate,
    UserCreateResponse,
    UserForAdmin,
    UserId,
    UserList,
    UserLogin,
    UserUpdate
)
import core.core_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


api_router = APIRouter(
    prefix="/api",
    tags=["api_user"]
)


oauth2_scheme = JwtAccessBearer(secret_key=SECRET_KEY, auto_error=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Защищенный эндпоинт

@api_router.get("/protected-endpoint")
def protected_endpoint(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    logger.info("Received token: %s", token)
    user = get_current_user(token, db)
    if user is None:
        logger.warning("Unauthorized access attempt with token: %s", token)
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Используйте точечную нотацию для доступа к атрибутам пользователя
    logger.info("User  %s is authorized", user.login)  # Исправлено на user.login

    # Убедитесь, что вы возвращаете объект TokenData
    response_message = f"You are authorized as {user.login}"

    return response_message  # Возвращаем строку


@api_router.post("/user", response_model=UserCreateResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    if core.core_user.is_user_exist(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User  already exists'
        )
    return core.core_user.register_user(data)

# Эндпоинт для аутентификации пользователя
@api_router.post("/user/login_jwt", response_model=Token)
def user_login_jwt(data: UserLogin, db: Session = Depends(get_db)):
    auth_result = authenticate_user(db, data.login, data.password)   
    if auth_result:
        return {'token': auth_result['token']} 
      
    logger.warning("Неверные учетные данные для пользователя: %s", data.login)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Authentication error, incorrect credentials'
    )


@api_router.put("/user/me", response_model=UserForAdmin)
def update_user(data: UserUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    user = core.core_user.update_user_data(db, current_user, data)
    return UserForAdmin.from_orm(user)


@api_router.put('/user/{user_id}', response_model=UserForAdmin)
def put_user_id(user_id: int, user_update: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user is None:
        logger.warning("Unauthorized access attempt with token: %s", token)
        raise HTTPException(status_code=401, detail="Unauthorized")
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail='User ID must not be zero'
        )    
    user_put = core.core_user.search_user_by_id_put(user_update, user_id, db)
    if user_put:
        return user_put   
    if user_put == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid user '
        )


@api_router.delete('/user/{user_id}')
def delete_user_id(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail='User ID must not be zero'
        )    
    user_del = core.core_user.search_user_by_id_for_delete(UserId(id=user_id), db)
    if user_del:
        return user_del    
    if user_del == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid user '
        )  


# Эндпоинт для получения списка читателей (только для администраторов)
@api_router.get("/user/list", response_model=List[UserList])
def list_readers(user_id: int = None, user_login: str = None, user_email: str = None, 
                 db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')   
    result_list = core.core_user.search_list_users(SearchUsersList(id=user_id, login=user_login, email=user_email), db)
    return result_list



