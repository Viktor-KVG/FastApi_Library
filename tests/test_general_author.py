'''Тесты для API, отвечающего за список авторов, включая сценарии с пустым ответом, наличием данных и поиском по имени, 
   включен тест для проверки логина с некорректными учетными данными. Также CRUD отперации для автора.'''


from models import AuthorModel
from unittest.mock import MagicMock, patch
from conftest import client
from src.schemas import SearchAuthorsModel
from datetime import date


def test_get_authors_empty(mock_session):
    with patch('src.database.get_db', return_value=mock_session):
        mock_session.query.return_value.all.return_value = []
        
        response = client.get("/api/author/list/", params={"limit": 10, "offset": 0})
        
        assert response.status_code == 200


def test_get_authors_with_data(mock_session):
    with patch('src.database.get_db', return_value=mock_session):
        mock_authors = [
            AuthorModel(id=1, name="Author One", biography="Bio One", date_of_birth="1980-01-01"),
            AuthorModel(id=2, name="Author Two", biography="Bio Two", date_of_birth="1990-01-01"),
        ]
        mock_session.query.return_value.all.return_value = mock_authors

        response = client.get("/api/author/list/", params={"limit": 10, "offset": 0})

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
        response = client.get("/api/author/list/", params=search_params.dict())
        
        authors_list = response.json()
        assert response.status_code == 200
        assert isinstance(authors_list, list)
        

def test_user_register_and_login(mock_user_create, admin_jwt_token):
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

                # Сохраняем токен
                token = response_create.json()["token"]

                # Создание автора с токеном в заголовке
                with patch("core.core_author.register_author", return_value={
                    "id": 1,
                    "name": "test_author1",
                    "biography": "test_string",
                    "date_of_birth": "2025-01-31"
                }):
                    # Мок для проверки существования автора
                    with patch("core.core_author.is_author_exist", return_value=False):
                        # Мок для функции create_access_token
                        with patch("src.auth.auth_jwt.create_access_token", return_value=admin_jwt_token):
                            response_create_author = client.post("/api/author/",
                                json={"name": "test_author1","biography": "test_string",
                                      "date_of_birth": date(2025, 1, 31).isoformat()  # Преобразуем date в строку
                                      },
                                headers={"Authorization": f"Bearer {token}"}  # Передаем токен в заголовке
                            )
                            print(response_create_author.json())
                            assert response_create_author.status_code == 200
                            assert response_create_author.json() == {
                                "id": 1,
                                "name": "test_author1",
                                "biography": "test_string",
                                "date_of_birth": "2025-01-31"
                            }


def test_update_author_success(admin_jwt_token):
    # Мок для текущего автора (администратор)
    with patch("core.core_author.is_author_exist", return_value=False):

        response = client.put(
                "/api/author/1/",
                json={"name": "Updated Author Name","biography": "Updated biography",
                                      "date_of_birth": date(2025, 1, 31).isoformat()  # Преобразуем date в строку
                                      },
                headers={"Authorization": f"Bearer {admin_jwt_token}"}
                )
        print(response.json())
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Updated Author Name",
            "biography": "Updated biography",
            "date_of_birth": "2025-01-31"
            }


def test_update_author_not_found(admin_jwt_token):
    # Мок для текущего пользователя (администратор)
    with patch("src.auth.auth_jwt.get_current_user", return_value=MagicMock(is_admin=False)):
        # Мок для функции search_author_by_id_put
        with patch("core.core_author.search_author_by_id_put", return_value=False):
            # Шаг 1: Попытка обновления несуществующего автора
            response = client.put(
                "/api/author/9990000",
                json={
                    "name": "Updated sAuthor Name",
                    "biography": "Updated biography",
                    "date_of_birth": date(2025, 1, 31).isoformat()  # Преобразуем date в строку
                },
                headers={"Authorization": f"Bearer {admin_jwt_token}"}
            )
            print(response.json())
            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid author"}                  


def test_author_delete(admin_jwt_token):
    # Мок для функции (автор не существует)
    with patch("core.core_author.is_author_exist", return_value=False):
        # Мок для функции search_author_by_id_for_delete
        with patch("core.core_author.search_author_by_id_for_delete", return_value={'details': 'Author deleted'}):
            # Удаление автора
            response_delete = client.delete(f"/api/author/{1}", headers={"Authorization": f"Bearer {admin_jwt_token}"})                
            # Проверка статуса ответа
            assert response_delete.status_code == 200
            assert response_delete.json() == {'details': 'Author deleted'}             