'''Этот файл определяет эндпоинты для управления авторами в приложении, включая создание, редактирование, 
   удаление и получение списка авторов. Эндпоинты для создания, редактирования и удаления авторов защищены 
   и доступны только администраторам, в то время как эндпоинт для получения списка авторов доступен всем пользователям.'''

import logging
from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.auth_jwt import get_current_user
import core.core_author
from src.models import UserModel
from src.schemas import AuthorsModel, CreateAuthorsModel, SearchAuthorsModel
from src.database import get_db
from fastapi_jwt import JwtAccessBearer
from src.settings import SECRET_KEY

oauth2_scheme = JwtAccessBearer(secret_key=SECRET_KEY, auto_error=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


api_router = APIRouter(
    prefix="/api",
    tags=["api_uthors"]
)


# Эндпоинт для создания авторов(только для администраторов)
@api_router.post("/author/", response_model=AuthorsModel)
def create_author_view(author: CreateAuthorsModel, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource') 
    if core.core_author.is_author_exist(author, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Author already exists'
            )
    return core.core_author.register_author(db=db, data=author)


# Эндпоинт для редактирования авторов(только для администраторов)
@api_router.put('/author/{author_id}', response_model=AuthorsModel)
def put_author_id(author_id: int, user_update: CreateAuthorsModel, 
                  current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    if author_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail='Author ID must not be zero'
        )    
    author_put = core.core_author.search_author_by_id_put(user_update, author_id, db)
    if author_put:
        return author_put   
    if author_put == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid author '
        )


# Эндпоинт для удаления авторов(только для администраторов)
@api_router.delete('/author/{author_id}')
def delete_author_id(author_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    if author_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail='User ID must not be zero'
        )    
    author_del = core.core_author.search_author_by_id_for_delete(author_id, db)
    if author_del:
        return author_del    
    if author_del == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid author '
        ) 
    

# Эндпоинт для получения списка авторов 
@api_router.get("/author/list", response_model=List[AuthorsModel])
def list_authors(author_id: int = None, author_name: str = None, limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    result_list = core.core_author.search_list_authors(
        SearchAuthorsModel(id=author_id, name=author_name, limit=limit, offset=offset),  
        db
    )
    return result_list 