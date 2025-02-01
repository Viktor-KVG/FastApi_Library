'''Фикстуры для тестирования функций, связанных с пользователями, включая создание, обновление и поиск пользователей.
   Используются мок-объекты для имитации взаимодействия с базой данных.'''

import jwt
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from settings import ALGORITHM, SECRET_KEY
from src.database import get_db
from schemas import  CreateBookModel, SearchUsersList, UserCreate, UserId, UserUpdate
from src.main import app 
from src.models import UserModel
from sqlalchemy.orm import Session
import logging


client = TestClient(app)

mock_session_db = MagicMock()

def override_get_db():
    try:
        yield mock_session_db
    finally:
        pass   

app.dependency_overrides[get_db] = override_get_db     



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_session():
    logger.info("Создание мока для сессии базы данных.")
    session = MagicMock(spec=Session)
    yield session
    logger.info("Завершение работы мока для сессии базы данных.")


@pytest.fixture
def mock_create_user():
    session = MagicMock(spec=Session)
    user = MagicMock()
    user.id = 1  # Установите id для мок-объекта
    user.login = 'testuser'
    user.email = 'test@example.com'
    user.is_admin = False
    session.add = MagicMock(return_value=None)
    session.commit = MagicMock(return_value=None)
    session.refresh = MagicMock(side_effect=lambda u: setattr(u, 'id', user.id))
    return session, user


@pytest.fixture
def mock_user_create():
    return UserCreate(login="test_user",
    password="test_password",
    email="test@example.com",
    is_admin=False)


@pytest.fixture
def mock_book_create():
    return CreateBookModel(
            title="test title",
            description="test description",
            author_id= 1,
            genre='genre',
            quantity= 1,
            )


@pytest.fixture
def mock_book_update():
    return CreateBookModel(
            title="test update title",
            description="test update description",
            author_id= 1,
            genre='triller',
            quantity= 1,
            )


@pytest.fixture
def admin_jwt_token():
    """Фикстура для генерации JWT-токена для администратора."""
    payload = {
        "subject": "test_admin_user",
        "is_admin": True
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def mock_user_update():
    return UserUpdate(login="updateduser", 
                      email="updated@example.com", 
                      password="newpassword", 
                      is_admin=False)


@pytest.fixture
def mock_user_id():
    return UserId(id=1)


@pytest.fixture
def mock_search_users_list():
    return SearchUsersList(id=None, 
                           login=None, 
                           email=None, 
                           limit=10, 
                           offset=0)


@pytest.fixture
def mock_user_model():
    from datetime import datetime
    user = UserModel(
        id=1,
        login="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_admin=False,
        created_at=datetime.now(), 
        updated_at=datetime.now()    
    )
    return user