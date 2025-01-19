
from datetime import datetime
from hashlib import md5
import logging
from fastapi import HTTPException, status
from src.auth import auth_jwt
from src.models import AuthorModel, BookModel, UserModel
from src.schemas import (
                         AuthorsModel,
                         BooksModel,
                         CreateAuthorsModel,
                         SearchAuthorsModel,
                         UserCreate,
                         UserId, 
                         UserLogin, 
                         UserCreateResponse,
                         UserList, 
                         UserUpdate,
                         SearchUsersList,
                         )
from src.database import session_factory
from sqlalchemy.orm import Session


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_author_exist(data: CreateAuthorsModel, db: Session) -> bool:
    same_author = db.query(AuthorModel).where(AuthorModel.name == data.name).first() is not None
    return same_author


def register_author(data: CreateAuthorsModel, db: Session) -> AuthorsModel:
    try:
        db_author = AuthorModel(**data.dict())
        db.add(db_author)
        db.commit()
        db.refresh(db_author)
        return db_author
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        

def search_author_by_id_put(data:CreateAuthorsModel, author_id:int, db: Session):
    query = db.query(AuthorModel).filter(AuthorModel.id == author_id).first()
    if query:
        query.name = data.name
        query.biography = data.biography
        query.date_of_birth = data.date_of_birth
        db.commit()
        db.refresh(query)
        return query
    return False 


def search_author_by_id_for_delete(author_id:int, db: Session):
    query = db.query(AuthorModel).filter(AuthorModel.id == author_id).first()
    if query:
        db.delete(query)
        db.commit()
        return{'details': 'Author deleted'}
    return False


def search_list_authors(data: SearchAuthorsModel, db: Session) -> list:
    query = db.query(AuthorModel)
    # Добавим условия к запросу, если они указаны
    if data.id is not None:
        query = query.filter(AuthorModel.id == data.id)
    if data.name:
        query = query.filter(AuthorModel.name == data.name)
    filtered_authors = query.all()            
    return filtered_authors

