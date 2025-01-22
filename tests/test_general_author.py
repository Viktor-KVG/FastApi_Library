'''Тесты для API, отвечающего за список авторов, включая сценарии с пустым ответом, наличием данных и поиском по имени.
   Также включен тест для проверки логина с некорректными учетными данными.'''

from models import AuthorModel
from unittest.mock import patch
from conftest import client
from src.schemas import SearchAuthorsModel


def test_get_authors_empty(mock_session):
    with patch('src.database.get_db', return_value=mock_session):
        mock_session.query.return_value.all.return_value = []
        
        response = client.get("/api/author/list", params={"limit": 10, "offset": 0})
        
        assert response.status_code == 200


def test_get_authors_with_data(mock_session):
    with patch('src.database.get_db', return_value=mock_session):
        mock_authors = [
            AuthorModel(id=1, name="Author One", biography="Bio One", date_of_birth="1980-01-01"),
            AuthorModel(id=2, name="Author Two", biography="Bio Two", date_of_birth="1990-01-01"),
        ]
        mock_session.query.return_value.all.return_value = mock_authors

        response = client.get("/api/author/list", params={"limit": 10, "offset": 0})

        assert response.status_code == 200
        assert isinstance(response.json(), list)  # Проверяем, что ответ - это список


def test_search_authors(mock_session):
    # Подменяем зависимость get_db на наш мок
    with patch('src.database.get_db', return_value=mock_session):
        # Создаем тестовые данные
        mock_authors = [
            AuthorModel(id=1, name="Author One", biography="Bio One", date_of_birth="1980-01-01"),
            AuthorModel(id=2, name="Author Two", biography="Bio Two", date_of_birth="1990-01-01"),
        ]

        # Настраиваем мок для поиска авторов по имени
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_authors[0]]

        search_params = SearchAuthorsModel(name="Author One", limit=10, offset=0)
        response = client.get("/api/author/list", params=search_params.dict())
        
        authors_list = response.json()
        assert response.status_code == 200
        assert isinstance(authors_list, list)


def test_login_invalid_credentials():
    response = client.post("/api/user/login_jwt", json={"login": "wronguser", "password": "wrongpassword"})
    
    assert response.status_code == 400
    assert response.json() == {"detail": "Authentication error, incorrect credentials"}

