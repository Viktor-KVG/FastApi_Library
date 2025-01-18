import logging
from fastapi import Depends, HTTPException, logger, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from hashlib import md5
from sqlalchemy.orm import Session
import fastapi_jwt
import jwt
from fastapi.encoders import jsonable_encoder
from src.schemas import UserInDB, UserLogin
from src.models import UserModel
from src.database import get_db, session_factory
import hashlib
from src.settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials

oauth2_scheme = JwtAccessBearer(secret_key=SECRET_KEY, auto_error=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
  


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()  # Копируем входные данные
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # Обновляем время истечения
    to_encode["subject"] = data.get("subject")

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 


def authenticate_user(db: Session, login: str, password: str):
    user = db.query(UserModel).filter(UserModel.login == login).first()
    if user:
        # Логируем хэш пароля
        logger.info("Проверяем хэш пароля для пользователя: %s", login)
        password_hash = md5(password.encode('utf-8')).hexdigest()
        logger.info("Введенный хэш пароля: %s, Хэш из БД: %s", password_hash, user.password_hash)
        
        if user.password_hash == password_hash:
            # Подготовка данных для токена
            token_data = {
                "subject": user.login,
                "is_admin": user.is_admin  
            }
            # Создание токена
            token = create_access_token(data=token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            return {'user': user, 'token': token}
    
    return None


def get_user(login: str, db: Session) -> UserInDB | None:
    logger.info(f"Получение пользователя с логином: {login}")
    logger.info(f"Тип db: {type(db)}")
    
    # Используем сессию базы данных для получения пользователя
    user = db.query(UserModel).filter(UserModel.login == login).first()
    
    if user:
        logger.info(f"Пользователь найден: {user}")
        return user
    else:
        logger.warning(f"Пользователь с логином {login} не найден в базе данных.")
        return None

def get_current_user(token: JwtAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.info(f"Тип db: {type(db)}")
    logger.info("Получение текущего пользователя из токена...")
    
    try:
        username: str = token.subject  # Предполагается, что в subject есть поле "login"
        
        if not username:  # Проверяем, что username не пустой
            logger.warning("Не удалось извлечь имя пользователя из токена.")
            raise credentials_exception
        
        logger.info(f"Проверка пользователя с логином: {username}")
        
        user = get_user(username, db)  # Передаем сессию базы данных

        if user is None:
            logger.warning("Пользователь не найден в базе данных.")
            raise credentials_exception
        
        logger.info("Пользователь успешно получен.")
        return user
    
    except Exception as e:
        logger.error("Ошибка при получении текущего пользователя", exc_info=True)
        raise credentials_exception
# def create_jwt_token(user_data: dict) -> str:
#     """Создание JWT токена на основе данных пользователя."""
#     return jwt.encode(user_data, SECRET_KEY, algorithm=ALGORITHM)


# def user_login(form_data: OAuth2PasswordRequestForm):
#     with session_factory() as session:
#         login_item_login = form_data.username  # Используйте username
#         login_item_password = hashlib.md5(form_data.password.encode('utf-8')).hexdigest()  # Используйте password
        
#         login_user = session.query(UserModel).filter_by(login=login_item_login).first()
        
#         if login_user and login_user.password_hash == login_item_password:
#             encoded_jwt = create_access_token({"sub": login_item_login})  # Используйте "sub" для идентификации пользователя
#             return encoded_jwt
#     return False

# def user_login(username: str, password: str):
#     """Аутентификация пользователя по логину и паролю."""
#     # Здесь должна быть ваша логика для проверки пользователя в базе данных
#     hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    
#     # Пример проверки пользователя (замените на вашу логику)
#     if username == "reader1" and hashed_password == hashlib.md5("password123".encode('utf-8')).hexdigest():
#         return create_jwt_token({"sub": username})
    
#     return False
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid authentication credentials")
#         return username  # Или возвращайте объект пользователя из базы данных
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=401, detail="Invalid authentication credentials")