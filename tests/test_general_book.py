''' Тесты для API, отвечающего за список книг, включая успешный запрос, пустой ответ и поиск по параметрам.
    Используются мок-объекты для имитации взаимодействия с базой данных через SQLAlchemy.
    Также тестирование CRUD отпераций для книг.'''

from unittest.mock import patch
from conftest import client
from models import BookModel


def test_list_books_success(mock_session):
    with patch('src.database.get_db', return_value=mock_session):
        mock_books = [
            BookModel(id=1, title="Book One", description="Description One", user_id=1, genre="Fiction", quantity=5),
            BookModel(id=2, title="Book Two", description="Description Two", user_id=1, genre="Non-Fiction", quantity=3),
        ]
        mock_session.query.return_value.all.return_value = mock_books
        
        response = client.get("/api/book/list/", params={"limit": 10, "offset": 0})
        
        books_list = response.json()  
        assert response.status_code == 200     
        assert isinstance(books_list, list)


def test_list_books_empty(mock_session):
    with patch('src.database.get_db', return_value=mock_session):
        mock_session.query.return_value.all.return_value = []
        
        response = client.get("/api/book/list/", params={"limit": 10, "offset": 0})

        books_list = response.json()        
        assert response.status_code == 200    
        assert isinstance(books_list, list)


def test_list_books_with_search_params(mock_session):
    with patch('src.database.get_db', return_value=mock_session):
        mock_books = [
            BookModel(id=1, title="Book One", description="Description One", user_id=1, genre="Fiction", quantity=5),
            BookModel(id=2, title="Book Two", description="Description Two", user_id=1, genre="Non-Fiction", quantity=3),
        ]
        
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_books[0]]
        
        response = client.get("/api/book/list", params={"book_title": "Book One", "limit": 10, "offset": 0})
        books_list = response.json()
        assert response.status_code == 200      
        assert isinstance(books_list, list)


def test_create_book(mock_book_create, admin_jwt_token):
    # Мок для функции (книга не существует)
    with patch("core.core_book.is_book_exist", return_value=False):
        # Мок для функции register_book
        with patch("core.core_book.register_book", return_value={
            "id": 1,
            "title": "test title",
            "description": "test description",
            "creator_id": 1,
            "genre": 'genre',
            "quantity": 1,
            "authors": [],
            }):

            response_create = client.post("/api/book/", json=mock_book_create.dict(), 
                                              headers={"Authorization": f"Bearer {admin_jwt_token}"})
            print(response_create.json())
            assert response_create.status_code == 200
            assert response_create.json() == {
                "id": 1,
                "title": "test title",
                "description": "test description",
                "creator_id": 1,
                "genre": 'genre',
                "quantity": 1,
                "authors": [],
                }
            

def test_update_book(mock_book_update, admin_jwt_token):
    # Мок для функции(книга не существует)
    with patch("core.core_book.is_book_exist", return_value=False):
        # Мок для функции search_book_by_id_put
        with patch("core.core_book.search_book_by_id_put", return_value={
            "id": 1,
            "title": "test update title",
            "description": "test update description",
            "creator_id": 1,
            "genre": 'triller',
            "quantity": 1,
            "authors": [],
            }):
            
            response_create = client.put("/api/book/1/", json=mock_book_update.dict(), 
                                         headers={"Authorization": f"Bearer {admin_jwt_token}"})
            print(response_create.json())
            assert response_create.status_code == 200
            assert response_create.json() == {
                "id": 1,
                "title": "test update title",
                "description": "test update description",
                "creator_id": 1,
                "genre": 'triller',
                "quantity": 1,
                "authors": [],
                }            


def test_book_delete(admin_jwt_token):
    # Мок для функции(книга не существует)
    with patch("core.core_book.is_book_exist", return_value=False):
        # Мок для функции search_book_by_id_for_delete
        with patch("core.core_book.search_book_by_id_for_delete", return_value={'details': 'Book deleted'}):
                # Удаление книги
            response_delete = client.delete(f"/api/book/{1}", headers={"Authorization": f"Bearer {admin_jwt_token}"})                
            # Проверка статуса ответа
            assert response_delete.status_code == 200
            assert response_delete.json() == {'details': 'Book deleted'}             