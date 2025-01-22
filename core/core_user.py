'''Файл отвечает за операции CRUD (создание, чтение, обновление и удаление)и поск для модели пользователей'''

from datetime import datetime
from hashlib import md5
import logging
from fastapi import HTTPException, status
from src.auth import auth_jwt
from src.models import AuthorModel, BookModel, UserModel
from src.schemas import (
                         AuthorsModel,
                         BooksModel,
                         UserCreate,
                         UserId, 
                         UserCreateResponse,
                         UserList, 
                         UserUpdate,
                         SearchUsersList,
                         )
from src.database import session_factory
from sqlalchemy.orm import Session


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_user_exist(data: UserCreate) -> bool:
    with session_factory() as session:
        same_user = session.query(UserModel).where(UserModel.login == data.login).first() is not None
        return same_user


def register_user(data: UserCreate, db: Session) -> UserCreateResponse:
    try:
        hashed_password = md5(data.password.encode('utf-8')).hexdigest()
        user = UserModel(
            password_hash=hashed_password,
            **data.model_dump(exclude={"password"})
        )
        db.add(user)
        db.commit()
        db.refresh(user)

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
        db.rollback()
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

    if data1.id is not None:
        query = query.filter(UserModel.id == data1.id)
    if data1.login:
        query = query.filter(UserModel.login == data1.login)
    if data1.email:
        query = query.filter(UserModel.email == data1.email)

    query = query.limit(data1.limit).offset(data1.offset)   
    filtered_users = query.all()            
    result_list = []
    for user in filtered_users:
        # Получение всех книг, связанных с этим пользователем
        books = db.query(BookModel).filter(BookModel.user_id == user.id).all()
        user_books = []
        for book in books:

            book_model = BooksModel.from_orm(book)
            # Получение авторов для каждой книги
            authors = db.query(AuthorModel).filter(AuthorModel.id == book.author_id).all()
            book_model.authors = [AuthorsModel.from_orm(author) for author in authors]  # Добавляем авторов
            user_books.append(book_model)
        
        # Создаем объект Pydantic для пользователя и добавляем списки книг
        user_list_item = UserList.from_orm(user)
        user_list_item.books = user_books  # Присваиваем выделенные книги
        # Добавляем пользователя с его книгами в результат
        result_list.append(user_list_item)   
    return result_list


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
