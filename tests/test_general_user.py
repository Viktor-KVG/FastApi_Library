'''Тесты для функций, связанных с пользователями, включая проверку существования пользователя, регистрацию, обновление данных и удаление.
   Используются мок-объекты для имитации взаимодействия с базой данных и создания JWT токенов.'''

from unittest.mock import MagicMock
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


def test_register_user(mock_create_user, mock_user_create):

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

   



   