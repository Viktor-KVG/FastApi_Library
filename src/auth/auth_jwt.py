'''Этот файл содержит функции для аутентификации пользователей и работы с JWT-токенами. 
   Он включает создание JWT-токена с заданным временем истечения, а также проверку учетных 
   данных пользователя при входе в систему. Функция get_user извлекает пользователя из 
   базы данных по логину, а get_current_user обеспечивает доступ к текущему пользователю 
   на основе токена аутентификации. Логирование используется для отслеживания процесса 
   аутентификации и выявления ошибок.'''

import logging
from fastapi import Depends, HTTPException, logger, status, HTTPException
from hashlib import md5
from sqlalchemy.orm import Session
import jwt
from src.schemas import UserInDB
from src.models import UserModel
from src.database import get_db
from src.settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials

oauth2_scheme = JwtAccessBearer(secret_key=SECRET_KEY, auto_error=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
  

# Создает и возвращает JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()  # Копируем входные данные
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # Обновляем время истечения
    to_encode["subject"] = data.get("subject")
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 


# Создание JWT токена по входящим данным
def authenticate_user(db: Session, login: str, password: str):
    logger.info(f"Начинаем аутентификацию для пользователя: {login}")
    user = db.query(UserModel).filter(UserModel.login == login).first()
    if user:
        logger.info(f"Пользователь найден: {login}")
        # Логируем хэш пароля
        logger.info(f"Проверяем хэш пароля для пользователя: {login}")
        password_hash = md5(password.encode('utf-8')).hexdigest()
        logger.info(f"Введенный хэш пароля: {password_hash}, Хэш из БД: {user.password_hash}")       
        if user.password_hash == password_hash:
            logger.info("Аутентификация успешна")
            # Подготовка данных для токена
            token_data = {
                "subject": user.login,
                "is_admin": user.is_admin  
            }
            # Создание токена
            token = create_access_token(data=token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            logger.info(f"Создан токен для пользователя: {login}")
            return {'user': user, 'token': token}
        logger.warning(f"Пользователь не найден: {login}")   
    return None


# Получение пользователя из базы данных
def get_user(login: str, db: Session) -> UserInDB | None:
    logger.info(f"Получение пользователя с логином: {login}")
    logger.info(f"Тип db: {type(db)}")
    user = db.query(UserModel).filter(UserModel.login == login).first()    
    if user:
        logger.info(f"Пользователь найден: {user}")
        return user
    else:
        logger.warning(f"Пользователь с логином {login} не найден в базе данных.")
        return None


# обеспечивает проверку и извлечение текущего пользователя на основе токена аутентификации
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
        if not username:
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
