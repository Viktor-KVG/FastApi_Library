'''Модели SQLAlchemy для управления пользователями, книгами, авторами и записями о займах в приложении.
   Определены четыре основные модели: UserModel, BookModel, AuthorModel и StorageModel.
   Каждая модель включает атрибуты и их типы, а также связи между моделями через отношения.
   Используются валидаторы для проверки статуса займов, а также указаны настройки для автоматического обновления временных меток.
   Эти модели обеспечивают структурированное представление данных и их взаимосвязей в базе данных.'''

from typing import List
from sqlalchemy import (
    func,
    String,
    DateTime,
    ForeignKey,
    Date
)
from sqlalchemy.orm import (
    Mapped,
    relationship,
    mapped_column,
    declarative_base, 
    validates
)

Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(60), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    email: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    books: Mapped[List["BookModel"]] = relationship("BookModel", back_populates="user", uselist=True)
    loans: Mapped[List["StorageModel"]] = relationship("StorageModel", back_populates="user", uselist=True)


class BookModel(Base):
    __tablename__ = 'book'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('author.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id')) 
    genre: Mapped[str] = mapped_column(String(120))
    quantity: Mapped[int] = mapped_column(nullable=True)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="books")
    author: Mapped["AuthorModel"] = relationship("AuthorModel", back_populates="books")
    loans: Mapped[List["StorageModel"]] = relationship("StorageModel", back_populates="book", uselist=True)

    @property
    def creator_id(self):
        return self.user_id  # Возвращает user_id как creator_id


class AuthorModel(Base):
    __tablename__ = 'author'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    biography: Mapped[str] = mapped_column(String(800))
    date_of_birth: Mapped[Date] = mapped_column(Date)

    books: Mapped[List["BookModel"]] = relationship("BookModel", back_populates="author", uselist=True)


class StorageModel(Base):
    __tablename__ = 'storage'

    STATUS_CHOICES = {'taken': 'Taken', 'returned': 'Returned'}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('book.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    loan_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    return_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='taken')

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="loans")
    book: Mapped["BookModel"] = relationship("BookModel", back_populates="loans")
   
    @validates('status')
    def validate_status(self, key, status):
        if status not in self.STATUS_CHOICES:
            raise ValueError(f"Invalid status: {status}")
        return status



