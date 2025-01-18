
import logging
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.auth_jwt import get_current_user
import core.core_author
from src.models import UserModel
from src.schemas import AuthorsModel, CreateAuthorsModel
from src.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


api_router = APIRouter(
    prefix="/api",
    tags=["api_uthors"]
)


@api_router.post("/authors/", response_model=AuthorsModel)
def create_author_view(author: CreateAuthorsModel, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    # user = get_current_user(current_user, db)
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource') 
    if core.core_author.is_author_exist(author, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Author already exists'
            )
    return core.core_author.register_author(db=db, data=author)