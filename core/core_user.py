from datetime import datetime
from hashlib import md5
import logging
from fastapi import HTTPException, status
from src.auth import auth_jwt
from src.models import BookModel, UserModel
from src.schemas import (
                         BooksModel,
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


'''User'''

def is_user_exist(data: UserCreate) -> bool:
    with session_factory() as session:
        same_user = session.query(UserModel).where(UserModel.login == data.login).first() is not None
        return same_user


def register_user(data: UserCreate) -> UserCreateResponse:
    with session_factory() as session:
        try:
            hashed_password = md5(data.password.encode('utf-8')).hexdigest()
            user = UserModel(
                password_hash=hashed_password,
                **data.model_dump(exclude={"password"})
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            # Создание JWT токена после успешной регистрации
            user_data = {
            "subject": user.login,
            "is_admin": user.is_admin 
            }
            token = auth_jwt.create_access_token(user_data)
            return UserCreateResponse(
                id=user.id,
                login=user.login,
                email=user.email,
                is_admin=user.is_admin,
                token=token
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

     
def search_user_by_id_put(data:UserUpdate, user_id:int, db: Session):
    query = db.query(UserModel).filter(UserModel.id == user_id).first()
    query_login = db.query(UserModel).filter(UserModel.login == data.login).first()
    if query_login:
        raise HTTPException(status_code=400, detail="Login already in use")
    if query:
        query.login = data.login
        query.password = data.password
        if data.password:
            hashed_password = md5(data.password.encode('utf-8')).hexdigest()
            query.password_hash = hashed_password
        query.email = data.email
        query.updated_at = datetime.now()
        db.commit()
        db.refresh(query)
        return query
    return False


def search_list_users(data1: SearchUsersList, db: Session) -> list:
    query = db.query(UserModel)
    # Добавим условия к запросу, если они указаны
    if data1.id is not None:
        query = query.filter(UserModel.id == data1.id)
    if data1.login:
        query = query.filter(UserModel.login == data1.login)
    if data1.email:
        query = query.filter(UserModel.email == data1.email)
    filtered_users = query.all()            
    result_list = []
    for user in filtered_users:
        # Получение всех книг, связанных с этим пользователем
        books = db.query(BookModel).filter(BookModel.author_id == user.id).all()       
        # Преобразование в список Pydantic моделей BooksModel
        user_books = [BooksModel.from_orm(book) for book in books]       
        # Создаем объект Pydantic для пользователя и добавляем списки книг
        user_list_item = UserList.from_orm(user)
        user_list_item.books = user_books  # Присваиваем выделенные книги
        # Добавляем пользователя с его книгами в результат
        result_list.append(user_list_item)
    return result_list  # Возвращаем список пользователей с их книгами


def update_user_data(db: Session, current_user: UserModel, data: UserUpdate) -> UserModel:
    logger.info(f'id вошедшего пользователя {current_user.id}')   
    # Обновляем данные текущего пользователя
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()   
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User  not found')
    user.login = data.login
    user.email = data.email
    if data.password:
        hashed_password = md5(data.password.encode('utf-8')).hexdigest()
        user.password_hash = hashed_password   
    db.commit()
    db.refresh(user)   
    return user


def search_user_by_id_for_delete(data: UserId, db: Session):
    user_delete = db.query(UserModel).filter(UserModel.id == data.id).first()
    if user_delete:
        db.delete(user_delete)
        db.commit()
        return{'details': 'User deleted'}
    return False
