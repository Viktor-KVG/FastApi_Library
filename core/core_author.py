
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


def is_author_exist(data: UserCreate, db: Session) -> bool:
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