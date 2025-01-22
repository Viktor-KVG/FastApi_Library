'''Этот файл определяет эндпоинты для управления заказами книг, включая выдачу книг пользователям, 
   возврат книг и получение всех займов конкретного пользователя. Все операции защищены, и доступ 
   к ним разрешен только администраторам, обеспечивая безопасность операций с книгами и их займом.'''

import logging
from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.auth_jwt import get_current_user
import core.core_storage
from src.models import StorageModel, UserModel
from src.schemas import OrdersModel
from src.database import get_db
from fastapi_jwt import JwtAccessBearer
from src.settings import SECRET_KEY

oauth2_scheme = JwtAccessBearer(secret_key=SECRET_KEY, auto_error=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_router = APIRouter(
    prefix="/api",
    tags=["api_storage"]
)


#Эндпоинт для выдачи книги пользователю
@api_router.post("/order/", response_model=OrdersModel)
def issue_book(user_id: int, book_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    
    logger.info(f"User  {current_user.id} is issuing a book.")
    return core.core_storage.issue_book_logic(user_id, book_id, db)


#Эндпоинт для возврата книги.
@api_router.post("/order/return/", response_model=OrdersModel)
def return_book(loan_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    return core.core_storage.return_book_logic(loan_id, db)


#Эндпоинт для получения всех займов (заказов) пользователя
@api_router.get("/order/{user_id}/users/", response_model=List[OrdersModel])
def get_user_loans(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    orders = db.query(StorageModel).filter(StorageModel.user_id == user_id).all()
    return orders

