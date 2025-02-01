'''Тесты для функций, связанных с пользователями, включая проверку существования пользователя, регистрацию, обновление данных и удаление.
   Используются мок-объекты для имитации взаимодействия с базой данных и создания JWT токенов.'''

from datetime import date
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from conftest import client
import logging
from core.core_user import (
    register_user,
    search_user_by_id_put,
    search_list_users,
    update_user_data,
    search_user_by_id_for_delete,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_register_user_with_token(mock_create_user, mock_user_create):
    mock_create_user, mock_user = mock_create_user

    # Мокаем создание JWT токена
    from src.auth import auth_jwt
    auth_jwt.create_access_token = MagicMock(return_value="mocked_token")

    logger.debug("Вызов функции регистрации пользователя")
    result = register_user(mock_user_create, db=mock_create_user)

    logger.debug("Проверка результата регистрации пользователя")
    assert result.id == mock_user.id
    assert result.login == mock_user_create.login
    assert result.email == mock_user_create.email
    assert result.is_admin == mock_user_create.is_admin
    assert result.token == "mocked_token"
    logger.debug("Тест успешно пройден")


def test_search_user_by_id_put(mock_session, mock_user_update, mock_user_model):
    # Настраиваем мок-сессию так, чтобы она возвращала пользователя с другим логином
    mock_session.query.return_value.filter.return_value.first.side_effect = [mock_user_model, None]   
    # Теперь вызываем функцию, которую мы тестируем
    result = search_user_by_id_put(mock_user_update, 1, mock_session)   
    # Здесь вы можете добавить дополнительные проверки, если необходимо
    assert result is not None  # или другие проверки, в зависимости от вашей логики


def test_search_list_users(mock_session, mock_search_users_list, mock_user_model):
    mock_session.query.return_value.limit.return_value.offset.return_value.all.return_value = [mock_user_model]

    result = search_list_users(mock_search_users_list, mock_session)

    assert len(result) == 1
    assert result[0].login == mock_user_model.login


def test_update_user_data(mock_session, mock_user_update, mock_user_model):
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user_model
    result = update_user_data(mock_session, mock_user_model, mock_user_update)

    assert result.login == mock_user_update.login
    assert result.email == mock_user_update.email


def test_search_user_by_id_for_delete(mock_session, mock_user_id, mock_user_model):
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user_model

    result = search_user_by_id_for_delete(mock_user_id, mock_session)

    assert result['details'] == 'User deleted'
    mock_session.delete.assert_called_once_with(mock_user_model)
    mock_session.commit.assert_called_once()

   
def test_user_register(mock_user_create, admin_jwt_token):
    # Мок для функции is_user_exist (пользователь не существует)
    with patch("core.core_user.is_user_exist", return_value=False):
        # Мок для функции register_user
        with patch("core.core_user.register_user", return_value={
            "id": 1,
            "login": "test_user1",
            "email": "test@example.com",
            "is_admin": True,
            "token": admin_jwt_token
            }):
            # Мок для create_access_token
            with patch("src.auth.auth_jwt.create_access_token", return_value=admin_jwt_token):
                # Создание пользователя
                response_create = client.post("/api/user/", json=mock_user_create.dict())
                print(response_create.json())
                assert response_create.status_code == 200
                assert response_create.json() == {
                    "id": 1,
                    "login": "test_user1",
                    "email": "test@example.com",
                    "is_admin": True,
                    "token": admin_jwt_token
                    }


def test_create_user_with_existing_login():
    # Предполагаем, что эндпоинт должен возвращать HTTPException с соответствующим сообщением
    user_data = {
        "login": "ExistingUser ",
        "password": "password",
        "email": "existing@example.com",
        "is_admin": False
    }

    # Мокаем функцию так, чтобы она выбрасывала HTTPException
    with patch("core.core_user.register_user", side_effect=HTTPException(status_code=400, 
                                                                         detail="User with this login already exists.")):
        # Вызываем эндпоинт создания пользователя
        response = client.post("/api/user/", json=user_data)

        # Проверяем, что возвращается ошибка
        assert response.status_code == 400
        assert response.json() == {"detail": "User with this login already exists."}
   

def test_user_login_invalid_password():
    # Мокируем функцию authenticate_user
    with patch('src.auth.auth_jwt.authenticate_user', return_value=None):
        response = client.post("/api/user/login_jwt/", json={"login": "TestUser_1", "password": "wrong_password"})

        # Проверяем статус код и содержимое ответа
        assert response.status_code == 400  # Неавторизован
        assert 'token' not in response.json() 


def test_user_login_user_not_found():
    # Мокируем функцию authenticate_user
    with patch('src.auth.auth_jwt.authenticate_user', return_value=None):
        response = client.post("/api/user/login_jwt/", json={"login": "TestUser_2", "password": "password"})

        # Проверяем статус код и содержимое ответа
        assert response.status_code == 400  # Неавторизован
        assert 'token' not in response.json()          


def test_login_invalid_credentials():
    response = client.post("/api/user/login_jwt/", json={"login": "wronguser", "password": "wrongpassword"})
    
    assert response.status_code == 400
    assert response.json() == {"detail": "Authentication error, incorrect credentials"}        


def test_user_update(mock_user_update, admin_jwt_token):
    # Мок для функции is_user_exist (пользователь не существует)
    with patch("core.core_user.is_user_exist", return_value=False):
        # Мок для функции register_user
        with patch("core.core_user.search_user_by_id_put", return_value={
            "id": 1,
            "login": "updateduser",
            "email": "updated@example.com",
            "created_at": date(2025, 1, 31).isoformat(),
            "updated_at": date(2025, 1, 31).isoformat(),
            "is_admin": False,
            "books": []
            }):
            response_create = client.put("/api/user/1/", json=mock_user_update.dict(), 
                                         headers={"Authorization": f"Bearer {admin_jwt_token}"})
            print(response_create.json())
            assert response_create.status_code == 200
            assert response_create.json() == {
                "id": 1,
                "login": "updateduser",
                "email": "updated@example.com",
                "created_at": "2025-01-31T00:00:00",
                "updated_at": "2025-01-31T00:00:00",
                "is_admin": False,
                "books": []
                }


def test_user_delete(admin_jwt_token):
    # Мок для функции is_user_exist (пользователь не существует)
    with patch("core.core_user.is_user_exist", return_value=False):
        # Мок для функции register_user
        with patch("core.core_user.search_user_by_id_for_delete", return_value={'details': 'User deleted'}):

            response_delete = client.delete(f"/api/user/{1}", headers={"Authorization": f"Bearer {admin_jwt_token}"})               
            # Проверка статуса ответа
            assert response_delete.status_code == 200
            assert response_delete.json() == {'details': 'User deleted'}   