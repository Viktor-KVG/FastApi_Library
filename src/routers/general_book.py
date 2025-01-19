import logging
from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.auth_jwt import get_current_user
import core.core_book
from src.models import AuthorModel, UserModel
from src.schemas import AuthorsModel, BooksModel, CreateAuthorsModel, CreateBookModel, SearchAuthorsModel, SearchBooksList
from src.database import get_db
from fastapi_jwt import JwtAccessBearer
from src.settings import SECRET_KEY

oauth2_scheme = JwtAccessBearer(secret_key=SECRET_KEY, auto_error=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


api_router = APIRouter(
    prefix="/api",
    tags=["api_books"]
)


# Эндпоинт для создания книг(только для администраторов)
@api_router.post("/book/", response_model=BooksModel)
def create_book_view(author: CreateBookModel, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource') 
    if core.core_book.is_book_exist(author, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Book already exists'
            )
    db_book = core.core_book.register_book(db=db, data=author, user_id=current_user.id)
    return BooksModel.from_orm(db_book)


# Эндпоинт для редактирования книг(только для администраторов)
@api_router.put('/book/{book_id}', response_model=BooksModel)
def put_book_id(book_id: int, book_update: CreateBookModel, 
                 current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    book_put = core.core_book.search_book_by_id_put(book_update, book_id, db)   
    if book_put is None:
        logger.error('Failed to update book, invalid user or book not found.')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid user or book not found')   
    return book_put
    

# Эндпоинт для удаления книги(только для администраторов)    
@api_router.delete('/book/{book_id}')
def delete_book_id(book_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')         
    book_del = core.core_book.search_book_by_id_for_delete(book_id, db)
    return book_del  


# Эндпоинт для получения списка книг (только для администраторов)
@api_router.get("/book/list", response_model=List[BooksModel])
def list_books(book_id: int = None, book_title: str = None, db: Session = Depends(get_db)):
    result_list = core.core_book.search_list_books(SearchBooksList(id=book_id, title=book_title),  db)
    return result_list 