import jwt
from fastapi.encoders import jsonable_encoder
from src.schemas import UserLogin
from src.models import UserModel
from src.database import session_factory
import hashlib
from src.settings import SECRET_KEY, ALGORITHM


def user_login(data: UserLogin):
    with session_factory() as session:
        login_item = jsonable_encoder(data)
        login_item_login = login_item['login']
        login_item_password = login_item['password']
        hashed_password = hashlib.md5(login_item_password.encode('utf-8')).hexdigest()
        login_user_token = session.query(UserModel.login).filter_by(login=login_item_login).first()     
        password_user_token = session.query(UserModel.password_hash).filter_by(password_hash=hashed_password).first()
    try:
        if login_item_login == login_user_token[0] and hashed_password == password_user_token[0]:
            encoded_jwt = jwt.encode(login_item, SECRET_KEY, algorithm=ALGORITHM)
            session.commit()
            return encoded_jwt
    except Exception as e:
        return False        


def create_jwt_token(user_data: dict) -> str:
    """Создание JWT токена на основе данных пользователя."""
    return jwt.encode(user_data, SECRET_KEY, algorithm=ALGORITHM)

