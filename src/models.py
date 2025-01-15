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
)

Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(60), nullable=False )
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    email: Mapped[str] = mapped_column(String(160), nullable=False) 
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    books: Mapped[List["BookModel"]] = relationship(back_populates="user", uselist=True)


class BookModel(Base):
    __tablename__ = 'book'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('author.id'))
    genre: Mapped[str] = mapped_column(String(120))
    quantity: Mapped[int] = mapped_column(nullable=True)
    reader: Mapped[List["UserModel"]] = relationship(back_populates="books", uselist=True)
    author: Mapped[List["AuthorModel"]] = relationship(back_populates="book", uselist=True)


class AuthorModel(Base):
    __tablename__ = 'author'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    biography: Mapped[str] = mapped_column(String(800))
    date_of_birth: Mapped[DateTime] = mapped_column(Date)
    book: Mapped[List["BookModel"]] = relationship(back_populates="author", uselist=True)



