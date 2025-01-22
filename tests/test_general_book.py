''' Тесты для API, отвечающего за список книг, включая успешный запрос, пустой ответ и поиск по параметрам.
    Используются мок-объекты для имитации взаимодействия с базой данных через SQLAlchemy.'''

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
        
        response = client.get("/api/book/list", params={"limit": 10, "offset": 0})
        
        books_list = response.json()  
        assert response.status_code == 200     
        assert isinstance(books_list, list)


def test_list_books_empty(mock_session):
    with patch('src.database.get_db', return_value=mock_session):
        mock_session.query.return_value.all.return_value = []
        
        response = client.get("/api/book/list", params={"limit": 10, "offset": 0})

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
