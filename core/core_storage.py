'''Этот файл содержит функции, отвечающие за логику выдачи и возврата книг'''

from datetime import datetime, timedelta
import logging
from fastapi import HTTPException
from src.models import BookModel, StorageModel, UserModel
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def issue_book_logic(user_id: int, book_id: int, db: Session):
    logger.info(f"Attempting to issue book {book_id} to user {user_id}")

    # Проверка, есть ли у пользователя уже 5 выданных книг
    current_order = db.query(StorageModel).filter(StorageModel.user_id == user_id, StorageModel.status == 'taken').count()
    logger.debug(f"Current orders for user {user_id}: {current_order}")
    
    if current_order >= 5:
        raise HTTPException(status_code=400, detail="User  has reached the limit of 5 borrowed books.")

    # Проверка, доступна ли книга для выдачи
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book or book.quantity <= 0:
        raise HTTPException(status_code=404, detail="Book not found or not available.")

    # Создание записи о взятии книги
    order = StorageModel(user_id=user_id, book_id=book_id, loan_date=datetime.now(), return_date=datetime.now() + timedelta(days=14))
    db.add(order)
    
    # Обновление количества книг
    book.quantity -= 1
    db.commit()
    db.refresh(order)
    db.refresh(book) 

    logger.info(f"Book {book_id} issued to user {user_id}. New quantity: {book.quantity}")
    return order


def return_book_logic(loan_id: int, db: Session):
    # Поиск записи о взятие книги
    order = db.query(StorageModel).filter(StorageModel.id == loan_id, StorageModel.status == 'taken').first()
    if not order:
        raise HTTPException(status_code=404, detail="Loan not found or already returned.")

    # Обновление статуса книги и количество доступных экземпляров книги
    order.status = 'returned'
    book = db.query(BookModel).filter(BookModel.id == order.book_id).first()
    book.quantity += 1  # Увеличиваем количество доступных экземпляров
    db.commit()
    db.refresh(order)

    return order

