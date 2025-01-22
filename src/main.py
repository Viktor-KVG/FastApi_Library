'''Основной файл приложения FastAPI, который инициализирует экземпляр приложения и подключает 
   маршрутизаторы для управления пользователями, авторами, книгами и записями о займах.
   Это позволяет организовать структуру API и разделить функциональность на отдельные модули.'''

from fastapi import FastAPI
from src.routers import general_user, general_author, general_book, general_storage

app = FastAPI()

app.include_router(general_user.api_router)
app.include_router(general_author.api_router)
app.include_router(general_book.api_router)
app.include_router(general_storage.api_router)