from hashlib import md5
import logging
from fastapi import HTTPException, status
from src.auth import auth_jwt
from src.models import BookModel, AuthorModel, UserModel
from src.schemas import (
                         UserCreate,
                         UserId, 
                         UserLogin, 
                         UserCreateResponse,
                         UserList, 
                         UserUpdate,
                         )
from src.database import session_factory


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


'''User'''

def is_user_exist(data: UserCreate) -> bool:
    with session_factory() as session:
        same_user = session.query(UserModel).where(UserModel.login == data.login).first() is not None
        if same_user:
            return True
        return False


def register_user(data: UserCreate) -> str:

    with session_factory() as session:
        try:
            hashed_password = md5()
            hashed_password.update(data.password.encode('utf-8'))
            user = UserModel(
                password_hash=hashed_password.hexdigest(),
                **data.model_dump(exclude={"password"})
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            # Создание JWT токена после успешной регистрации
            user_data = {"login": user.login}
            return auth_jwt.create_jwt_token(user_data)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))    



