'''Файл отвечает за операции CRUD (создание, чтение, обновление и удаление)и поск для модели книг'''

import logging
from fastapi import HTTPException, status
from src.models import AuthorModel, BookModel
from src.schemas import (
                         AuthorsModel,
                         BooksModel,
                         CreateBookModel,
                         SearchBooksList,
                         )
from sqlalchemy.orm import Session


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_book_exist(data: CreateBookModel, db: Session) -> bool:
    same_book = db.query(BookModel).where(BookModel.title == data.title).first() is not None
    return same_book


def register_book(data: CreateBookModel, db: Session, user_id: int) -> BooksModel:
    author = db.query(AuthorModel).filter(AuthorModel.id == data.author_id).first()
    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {data.author_id} does not exist.")
    try:
        db_book = BookModel(**data.dict(), user_id=user_id)
        db.add(db_book)
        db.commit()
        db.refresh(db_book)

        # Извлекаем авторов для возвращаемого объекта
        authors = db.query(AuthorModel).filter(AuthorModel.id == data.author_id).all()
        db_book.authors = [AuthorsModel.from_orm(author) for author in authors]
        return db_book
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        

def search_book_by_id_put(data: CreateBookModel, book_id: int, db: Session) -> BooksModel:
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail='Book ID must not be zero'
        )
    logger.info(f'Searching for book with ID: {book_id}')
    query = db.query(BookModel).filter(BookModel.id == book_id).first()    
    if query:
        logger.info(f'Found book: {query.title}')
        query.title = data.title
        query.description = data.description
        query.author_id = data.author_id
        query.genre = data.genre
        query.quantity = data.quantity
        db.commit()
        db.refresh(query)
        return query   
    logger.warning(f'Book with ID {book_id} not found')
    return None     


def search_book_by_id_for_delete(book_id: int, db: Session):
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail='Book ID must not be zero'
        )
    logger.info(f'Searching for book with ID: {book_id}')
    query = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not query:
        logger.warning(f'Book with ID {book_id} not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Book not found'
        )
    db.delete(query)
    db.commit()
    logger.info(f'Book with ID {book_id} deleted successfully')
    return {'details': 'Book deleted'}    


def search_list_books(data: SearchBooksList, db: Session) -> list:
    query = db.query(BookModel)
    
    # Добавим условия к запросу, если они указаны
    if data.id is not None:
        query = query.filter(BookModel.id == data.id)
    if data.title:
        query = query.filter(BookModel.title == data.title)

    # Применяем пагинацию
    filtered_books = query.offset(data.offset).limit(data.limit).all()          
    result_list = []

    for book in filtered_books:
        # Получение всех авторов, связанных с этой книгой
        authors = db.query(AuthorModel).filter(AuthorModel.id == book.author_id).all()
        
        # Преобразование в список Pydantic моделей AuthorModel
        book_authors = [AuthorsModel.from_orm(author) for author in authors]
        
        # Создаем объект Pydantic для книги и добавляем список авторов
        book_data = BooksModel.from_orm(book)
        book_data.authors = book_authors  # Присваиваем авторов

        # Добавляем книгу с её авторами в результат
        result_list.append(book_data)

    return result_list